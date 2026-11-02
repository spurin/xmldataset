"""The indented text profile syntax: parser and writer.

Grammar, one entry per line (blank lines and lines starting with ``#`` are
ignored)::

    name                          an element; indented lines below are inside it
    name = spec [spec ...]        a field (may also open a block, for attributes)
    name = __IGNORE__             skip this element entirely
    __DIRECTIVE__ = args          a directive for the enclosing element

    spec     = modifier[,modifier...]      e.g. dataset:books,name:book_title
    modifier = key:value                   value is bare, or "quoted" / 'quoted'
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from ._errors import ProfileError
from ._model import (
    DatasetProcess,
    ExternalReset,
    ExternalValue,
    Field,
    Node,
    Profile,
)

__all__ = ["parse_dsl", "profile_to_dsl"]

IGNORE = "__IGNORE__"
DIRECTIVES = (
    "__NEW_DATASET__",
    "__EXTERNAL_VALUE__",
    "__NEW_EXTERNAL_VALUE_HOLDER__",
    "__DATASET_PROCESSING__",
    "__ALWAYS_FOLLOW__",
)
MODIFIERS = (
    "dataset",
    "external_dataset",
    "name",
    "prefix",
    "process",
    "default",
    "list",
)

DIRECTIVE_NAME = re.compile(r"__[A-Z][A-Z0-9_]*__")
_NAME = re.compile(r"\{[^{}\s]*\}[^\s={}]+|[^\s={}$#][^\s={}]*")
_KEY = re.compile(r"[A-Za-z_]+")


def is_node_name(name: str) -> bool:
    """Whether ``name`` can be used as an element or attribute name in a profile."""
    return bool(_NAME.fullmatch(name)) and not DIRECTIVE_NAME.fullmatch(name)


def suggest(word: str, choices: tuple[str, ...]) -> str:
    match = difflib.get_close_matches(word, choices, n=1)
    return f" (did you mean {match[0]!r}?)" if match else ""


@dataclass
class _Builder:
    name: str
    line: int = 0
    ignore_line: int = 0
    fields: list[Field] = field(default_factory=list)
    children: dict[str, _Builder] = field(default_factory=dict)
    ignore: bool = False
    new_dataset: list[str] = field(default_factory=list)
    external_values: list[ExternalValue] = field(default_factory=list)
    resets: list[ExternalReset] = field(default_factory=list)
    processing: list[DatasetProcess] = field(default_factory=list)
    always_follow: list[tuple[str, int, int]] = field(default_factory=list)

    def child(self, name: str, line: int) -> _Builder:
        if name not in self.children:
            self.children[name] = _Builder(name, line)
        return self.children[name]

    def freeze(self) -> Node:
        if self.ignore and (
            self.fields
            or self.children
            or self.new_dataset
            or self.external_values
            or self.resets
            or self.processing
            or self.always_follow
        ):
            raise ProfileError(
                f"{self.name!r} is ignored, so it cannot also have fields or contents",
                line=self.ignore_line,
                column=1,
            )
        for name, line, column in self.always_follow:
            if name not in self.children:
                raise ProfileError(
                    f"__ALWAYS_FOLLOW__ names {name!r}, which is not an element"
                    f" inside {self.name!r}",
                    line=line,
                    column=column,
                )
        return Node(
            name=self.name,
            fields=tuple(self.fields),
            children=tuple(child.freeze() for child in self.children.values()),
            ignore=self.ignore,
            new_dataset=tuple(dict.fromkeys(self.new_dataset)),
            external_values=tuple(self.external_values),
            reset_external_values=tuple(self.resets),
            dataset_processing=tuple(self.processing),
            always_follow=tuple(dict.fromkeys(n for n, _, _ in self.always_follow)),
        )


class _Line:
    """Cursor over one profile line, for tokenising with column numbers."""

    def __init__(self, text: str, number: int, start: int) -> None:
        self.text = text
        self.number = number
        self.pos = start

    def error(self, message: str, pos: int | None = None) -> ProfileError:
        column = (self.pos if pos is None else pos) + 1
        return ProfileError(message, line=self.number, column=column)

    def at_end(self) -> bool:
        return self.pos >= len(self.text)

    def skip_spaces(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in " \t":
            self.pos += 1

    def read_value(self) -> str:
        """Read a bare value (up to whitespace or comma) or a quoted value."""
        text = self.text
        if self.pos < len(text) and text[self.pos] in "\"'":
            quote = text[self.pos]
            start = self.pos
            self.pos += 1
            out = []
            while self.pos < len(text):
                char = text[self.pos]
                # Only \" (or \') and \\ are escapes; other backslashes are literal.
                if char == "\\" and text[self.pos + 1 : self.pos + 2] in (quote, "\\"):
                    out.append(text[self.pos + 1])
                    self.pos += 2
                    continue
                if char == quote:
                    self.pos += 1
                    return "".join(out)
                out.append(char)
                self.pos += 1
            raise self.error("unterminated quoted value", start)
        start = self.pos
        while self.pos < len(text) and text[self.pos] not in " \t,":
            self.pos += 1
        return text[start : self.pos]


def _parse_specs(cur: _Line) -> list[Field]:
    specs: list[Field] = []
    while True:
        cur.skip_spaces()
        if cur.at_end():
            break
        spec_start = cur.pos
        values: dict[str, str] = {}
        while True:
            key_match = _KEY.match(cur.text, cur.pos)
            if not key_match or cur.text[key_match.end() : key_match.end() + 1] != ":":
                raise cur.error(
                    "expected key:value, such as dataset:books"
                    + (" (a field needs at least one key:value)" if not values else "")
                )
            key = key_match.group()
            if key not in MODIFIERS:
                raise cur.error(f"unknown key {key!r}{suggest(key, MODIFIERS)}")
            cur.pos = key_match.end() + 1
            value_start = cur.pos
            value = cur.read_value()
            if key in values and values[key] != value:
                raise cur.error(
                    f"{key!r} is given twice with different values", value_start
                )
            values[key] = value
            if cur.text[cur.pos : cur.pos + 1] == ",":
                cur.pos += 1
                continue
            break
        if "dataset" not in values and "external_dataset" not in values:
            raise cur.error("a field needs dataset: or external_dataset:", spec_start)
        as_list = values.get("list", "false").lower()
        if as_list not in ("true", "false"):
            raise cur.error("list: must be true or false", spec_start)
        for key in ("dataset", "external_dataset"):
            if key in values and (
                not values[key] or any(c.isspace() for c in values[key])
            ):
                raise cur.error(
                    f"{key} name must be non-empty and contain no spaces", spec_start
                )
        specs.append(
            Field(
                dataset=values.get("dataset"),
                external_dataset=values.get("external_dataset"),
                name=values.get("name"),
                prefix=values.get("prefix"),
                process=values.get("process"),
                default=values.get("default"),
                as_list=as_list == "true",
            )
        )
    if not specs:
        raise cur.error("expected at least one field after '='")
    return specs


def _parse_directive(builder: _Builder, directive: str, cur: _Line) -> None:
    cur.skip_spaces()
    items: list[tuple[str, int]] = []
    for match in re.finditer(r"\S+", cur.text[cur.pos :]):
        items.append((match.group(), cur.pos + match.start()))
    if not items:
        raise cur.error(f"{directive} needs at least one value")

    def parts(item: str, pos: int, counts: tuple[int, ...], form: str) -> list[str]:
        split = item.split(":")
        if len(split) not in counts or not all(split):
            raise cur.error(f"expected {form}, got {item!r}", pos)
        return split

    for item, pos in items:
        if directive == "__NEW_DATASET__":
            builder.new_dataset.append(item)
        elif directive == "__ALWAYS_FOLLOW__":
            builder.always_follow.append((item, cur.number, pos + 1))
        elif directive == "__EXTERNAL_VALUE__":
            p = parts(item, pos, (3, 4), "external_dataset:field:dataset[:name]")
            builder.external_values.append(
                ExternalValue(p[0], p[1], p[2], p[3] if len(p) == 4 else None)
            )
        elif directive == "__NEW_EXTERNAL_VALUE_HOLDER__":
            p = parts(item, pos, (2,), "external_dataset:field")
            builder.resets.append(ExternalReset(p[0], p[1]))
        else:  # __DATASET_PROCESSING__
            p = parts(item, pos, (2,), "process:dataset")
            builder.processing.append(DatasetProcess(p[0], p[1]))


def parse_dsl(text: str) -> Profile:
    """Compile a profile written in the indented text syntax.

    Raises:
        ProfileError: The profile is invalid. ``line`` and ``column`` locate
            the problem.
    """
    if not isinstance(text, str):
        raise TypeError(f"a text profile must be str, not {type(text).__name__}")
    root = _Builder("")
    stack: list[tuple[int, _Builder]] = []  # (indentation, block receiving entries)
    opener: _Builder | None = None  # entry on the previous line that may open a block
    indent_char = ""
    base = -1

    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        body = line.lstrip(" \t")
        if not body or body.startswith("#"):
            continue
        indent = len(line) - len(body)
        chars = set(line[:indent])
        if len(chars) > 1:
            raise ProfileError(
                "indentation mixes tabs and spaces", line=number, column=1
            )
        if chars:
            char = chars.pop()
            if indent_char and char != indent_char:
                raise ProfileError(
                    "indentation uses tabs and spaces inconsistently",
                    line=number,
                    column=1,
                )
            indent_char = char

        if base < 0:
            base = indent
            stack = [(indent, root)]
        if indent < base:
            raise ProfileError(
                "line is indented less than the first line of the profile",
                line=number,
                column=1,
            )
        if indent > stack[-1][0]:
            if opener is None:
                raise ProfileError(
                    "unexpected indentation", line=number, column=indent + 1
                )
            stack.append((indent, opener))
        elif indent < stack[-1][0]:
            while stack[-1][0] > indent:
                stack.pop()
            if stack[-1][0] != indent:
                raise ProfileError(
                    "unindent does not match any outer indentation level",
                    line=number,
                    column=indent + 1,
                )
        block = stack[-1][1]
        cur = _Line(line, number, indent)
        opener = None

        name_match = _NAME.match(line, indent)
        if not name_match:
            raise cur.error("expected an element name")
        name = name_match.group()
        cur.pos = name_match.end()
        cur.skip_spaces()
        has_value = not cur.at_end()
        if has_value:
            if line[cur.pos] != "=":
                raise cur.error("expected '=' or the end of the line")
            cur.pos += 1

        if DIRECTIVE_NAME.fullmatch(name):
            if name not in DIRECTIVES:
                raise ProfileError(
                    f"unknown directive {name!r}{suggest(name, DIRECTIVES)}",
                    line=number,
                    column=indent + 1,
                )
            if block is root:
                raise ProfileError(
                    f"{name} must be inside an element", line=number, column=indent + 1
                )
            if not has_value:
                raise cur.error(f"{name} needs '=' and a value")
            _parse_directive(block, name, cur)
            continue

        child = block.child(name, number)
        if not has_value:
            opener = child
            continue
        cur.skip_spaces()
        if line[cur.pos :] == IGNORE:
            child.ignore = True
            child.ignore_line = number
            continue
        child.fields.extend(_parse_specs(cur))
        opener = child

    if not root.children:
        raise ProfileError("the profile is empty")
    return Profile(tuple(child.freeze() for child in root.children.values()))


# --- writer ------------------------------------------------------------------


LINE_BREAKS = frozenset("\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029")  # as str.splitlines


def quote(value: str) -> str:
    """Quote a modifier value if the bare form would not read back the same."""
    if LINE_BREAKS.intersection(value):
        raise ProfileError(
            f"value {value!r} contains a line break, which the text syntax cannot hold"
        )
    if (
        value
        and not any(c.isspace() or c == "," for c in value)
        and value[0] not in "\"'"
    ):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _spec_text(spec: Field) -> str:
    out = []
    for key, value in (
        ("dataset", spec.dataset),
        ("external_dataset", spec.external_dataset),
        ("name", spec.name),
        ("prefix", spec.prefix),
        ("process", spec.process),
        ("default", spec.default),
    ):
        if value is not None:
            out.append(f"{key}:{quote(value)}")
    if spec.as_list:
        out.append("list:true")
    return ",".join(out)


def _directive_part(value: str, what: str) -> str:
    if not value or ":" in value or any(c.isspace() for c in value):
        raise ProfileError(
            f"{what} {value!r} cannot be written in the text syntax"
            " (it must be non-empty, with no spaces or colons)"
        )
    return value


def profile_to_dsl(profile: Profile, indent: str = "    ") -> str:
    """Return ``profile`` in the indented text syntax."""
    lines: list[str] = []

    def emit(node: Node, depth: int) -> None:
        pad = indent * depth
        inner = indent * (depth + 1)
        if not is_node_name(node.name):
            raise ProfileError(f"element name {node.name!r} cannot be written as text")
        if node.ignore:  # the model guarantees an ignored node has nothing else
            lines.append(f"{pad}{node.name} = {IGNORE}")
            return
        if node.fields:
            lines.append(
                f"{pad}{node.name} = " + " ".join(map(_spec_text, node.fields))
            )
        else:
            lines.append(f"{pad}{node.name}")
        if node.new_dataset:
            for name in node.new_dataset:
                if not name or any(c.isspace() for c in name):
                    raise ProfileError(f"dataset name {name!r} cannot contain spaces")
            lines.append(f"{inner}__NEW_DATASET__ = " + " ".join(node.new_dataset))
        if node.always_follow:
            lines.append(f"{inner}__ALWAYS_FOLLOW__ = " + " ".join(node.always_follow))
        if node.reset_external_values:
            items = [
                ":".join(
                    _directive_part(p, "name") for p in (r.external_dataset, r.field)
                )
                for r in node.reset_external_values
            ]
            lines.append(f"{inner}__NEW_EXTERNAL_VALUE_HOLDER__ = " + " ".join(items))
        for child in node.children:
            emit(child, depth + 1)
        if node.external_values:
            items = []
            for ext in node.external_values:
                parts = [ext.external_dataset, ext.field, ext.dataset]
                if ext.name is not None:
                    parts.append(ext.name)
                items.append(":".join(_directive_part(p, "name") for p in parts))
            lines.append(f"{inner}__EXTERNAL_VALUE__ = " + " ".join(items))
        if node.dataset_processing:
            items = [
                ":".join(_directive_part(p, "name") for p in (d.process, d.dataset))
                for d in node.dataset_processing
            ]
            lines.append(f"{inner}__DATASET_PROCESSING__ = " + " ".join(items))

    for root in profile.roots:
        emit(root, 0)
    return "\n".join(lines) + "\n"
