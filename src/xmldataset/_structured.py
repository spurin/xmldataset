"""Structured profiles: YAML, JSON and plain mappings.

Keys starting with ``$`` describe the element they are written in; every other
key is a child element or attribute. XML names cannot start with ``$``, so the
two never collide::

    catalog:
      book:
        id: books                              # shorthand: dataset name only
        author: {$dataset: books, $process: upper}
        title: [books, {dataset: titles, name: book_title}]
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Any

from ._dsl import is_node_name, parse_dsl, suggest
from ._errors import ProfileError
from ._model import DatasetProcess, ExternalReset, ExternalValue, Field, Node, Profile

__all__ = [
    "dump_yaml",
    "load_profile",
    "load_yaml",
    "profile_from_dict",
    "profile_to_dict",
]

SPEC_KEYS = (
    "dataset",
    "external_dataset",
    "name",
    "prefix",
    "process",
    "default",
    "list",
)
NODE_KEYS = (
    *(f"${key}" for key in SPEC_KEYS),
    "$fields",
    "$ignore",
    "$new_dataset",
    "$always_follow",
    "$external_values",
    "$reset_external_values",
    "$dataset_processing",
)


def _err(message: str, loc: str) -> ProfileError:
    return ProfileError(message, location=loc)


def _text(value: Any, loc: str, what: str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    raise _err(f"{what} must be a string, not {type(value).__name__} (quote it)", loc)


def _name(value: Any, loc: str, what: str) -> str:
    text = _text(value, loc, what)
    if not text or any(c.isspace() for c in text):
        raise _err(f"{what} must be non-empty and contain no spaces", loc)
    return text


def _names(value: Any, loc: str, what: str) -> tuple[str, ...]:
    items = value if isinstance(value, list) else [value]
    return tuple(_name(item, f"{loc}[{i}]", what) for i, item in enumerate(items))


def _keys_are_strings(values: Mapping[Any, Any], loc: str) -> None:
    for key in values:
        if not isinstance(key, str):
            raise _err(
                f"keys must be strings, not {type(key).__name__} (quote it; YAML reads"
                " yes/no/on/off as booleans)",
                loc,
            )


def _records(
    value: Any, loc: str, keys: tuple[str, ...], optional: tuple[str, ...] = ()
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        value = [value]
    out = []
    for i, item in enumerate(value):
        where = f"{loc}[{i}]"
        if not isinstance(item, Mapping):
            raise _err(f"expected a mapping with keys {', '.join(keys)}", where)
        _keys_are_strings(item, where)
        for key in item:
            if key not in keys and key not in optional:
                raise _err(
                    f"unknown key {key!r}{suggest(str(key), keys + optional)}", where
                )
        missing = [key for key in keys if key not in item]
        if missing:
            raise _err(f"missing {', '.join(missing)}", where)
        out.append({key: _name(item[key], where, key) for key in item})
    return out


def _spec(values: Mapping[str, Any], loc: str, prefix: str = "") -> Field:
    _keys_are_strings(values, loc)
    for key in values:
        if key.removeprefix(prefix) not in SPEC_KEYS:
            choices = tuple(prefix + k for k in SPEC_KEYS)
            raise _err(f"unknown key {key!r}{suggest(str(key), choices)}", loc)
    get = {key.removeprefix(prefix): value for key, value in values.items()}
    if "dataset" not in get and "external_dataset" not in get:
        raise _err(f"a field needs {prefix}dataset or {prefix}external_dataset", loc)
    as_list = get.get("list", False)
    if not isinstance(as_list, bool):
        raise _err(f"{prefix}list must be true or false", loc)
    texts = {
        key: _text(get[key], loc, prefix + key)
        for key in ("name", "prefix", "process", "default")
        if key in get
    }
    return Field(
        dataset=_name(get["dataset"], loc, "dataset") if "dataset" in get else None,
        external_dataset=(
            _name(get["external_dataset"], loc, "external_dataset")
            if "external_dataset" in get
            else None
        ),
        as_list=as_list,
        **texts,
    )


def _field(item: Any, loc: str) -> Field:
    if isinstance(item, Mapping):
        return _spec(item, loc)
    return Field(dataset=_name(item, loc, "dataset"))


def _node(name: Any, value: Any, loc: str) -> Node:
    if not isinstance(name, str) or not is_node_name(name):
        raise _err(f"{name!r} is not a valid element or attribute name", loc)
    if value is None:
        return Node(name)
    if isinstance(value, list):
        if not value:
            raise _err("expected at least one field", loc)
        return Node(
            name,
            fields=tuple(_field(item, f"{loc}[{i}]") for i, item in enumerate(value)),
        )
    if not isinstance(value, Mapping):
        return Node(name, fields=(_field(value, loc),))

    for key in value:
        if not isinstance(key, str):
            raise _err(
                f"keys must be strings, not {type(key).__name__} (quote it; YAML reads"
                " yes/no/on/off as booleans)",
                loc,
            )
        if key.startswith("$") and key not in NODE_KEYS:
            raise _err(f"unknown setting {key!r}{suggest(key, NODE_KEYS)}", loc)
    fields: list[Field] = []
    shorthand = {
        key: v for key, v in value.items() if key[1:] in SPEC_KEYS and key[0] == "$"
    }
    if shorthand:
        fields.append(_spec(shorthand, loc, prefix="$"))
    if "$fields" in value:
        items = value["$fields"]
        if not isinstance(items, list) or not items:
            raise _err("$fields must be a non-empty list", loc)
        fields.extend(
            _field(item, f"{loc} > $fields[{i}]") for i, item in enumerate(items)
        )
    ignore = value.get("$ignore", False)
    if not isinstance(ignore, bool):
        raise _err("$ignore must be true or false", loc)

    children = tuple(
        _node(key, child, f"{loc} > {key}")
        for key, child in value.items()
        if not key.startswith("$")
    )
    always_follow = (
        _names(value["$always_follow"], f"{loc} > $always_follow", "element name")
        if "$always_follow" in value
        else ()
    )
    if ignore and len(value) > 1:
        raise _err(
            f"{name!r} is ignored, so it cannot also have fields or contents", loc
        )
    child_names = {child.name for child in children}
    for follow in always_follow:
        if follow not in child_names:
            raise _err(
                f"$always_follow names {follow!r},"
                f" which is not an element inside {name!r}",
                loc,
            )

    def records(
        key: str, keys: tuple[str, ...], optional: tuple[str, ...] = ()
    ) -> list[dict[str, str]]:
        return (
            _records(value[key], f"{loc} > {key}", keys, optional)
            if key in value
            else []
        )

    return Node(
        name=name,
        fields=tuple(fields),
        children=children,
        ignore=ignore,
        new_dataset=(
            tuple(
                dict.fromkeys(
                    _names(value["$new_dataset"], f"{loc} > $new_dataset", "dataset")
                )
            )
            if "$new_dataset" in value
            else ()
        ),
        external_values=tuple(
            ExternalValue(
                r["external_dataset"], r["field"], r["dataset"], r.get("name")
            )
            for r in records(
                "$external_values", ("external_dataset", "field", "dataset"), ("name",)
            )
        ),
        reset_external_values=tuple(
            ExternalReset(r["external_dataset"], r["field"])
            for r in records("$reset_external_values", ("external_dataset", "field"))
        ),
        dataset_processing=tuple(
            DatasetProcess(r["process"], r["dataset"])
            for r in records("$dataset_processing", ("process", "dataset"))
        ),
        always_follow=tuple(dict.fromkeys(always_follow)),
    )


def profile_from_dict(data: Mapping[str, Any]) -> Profile:
    """Compile a profile from a mapping, such as loaded YAML or JSON.

    Raises:
        ProfileError: The profile is invalid. ``location`` says where.
    """
    if not isinstance(data, Mapping):
        raise _err(f"a profile must be a mapping, not {type(data).__name__}", "profile")
    roots = []
    for key, value in data.items():
        if key == "$schema":
            continue
        if isinstance(key, str) and key.startswith("$"):
            raise _err(f"unknown top-level setting {key!r}", "profile")
        roots.append(_node(key, value, str(key)))
    if not roots:
        raise _err("the profile is empty", "profile")
    return Profile(tuple(roots))


def _spec_value(spec: Field) -> str | dict[str, Any]:
    out: dict[str, Any] = {
        key: value
        for key, value in (
            ("dataset", spec.dataset),
            ("external_dataset", spec.external_dataset),
            ("name", spec.name),
            ("prefix", spec.prefix),
            ("process", spec.process),
            ("default", spec.default),
        )
        if value is not None
    }
    if spec.as_list:
        out["list"] = True
    if list(out) == ["dataset"]:
        return out["dataset"]  # type: ignore[no-any-return]
    return out


def _node_value(node: Node) -> Any:
    has_body = bool(
        node.children
        or node.ignore
        or node.new_dataset
        or node.external_values
        or node.reset_external_values
        or node.dataset_processing
        or node.always_follow
    )
    if not has_body:
        if not node.fields:
            return None
        items = [_spec_value(spec) for spec in node.fields]
        if len(items) > 1:
            return items
        item = items[0]
        return (
            item if isinstance(item, str) else {f"${key}": v for key, v in item.items()}
        )
    out: dict[str, Any] = {}
    if len(node.fields) == 1:
        value = _spec_value(node.fields[0])
        spec = {"dataset": value} if isinstance(value, str) else value
        out.update({f"${key}": v for key, v in spec.items()})
    elif node.fields:
        out["$fields"] = [_spec_value(spec) for spec in node.fields]
    if node.ignore:
        out["$ignore"] = True
    if node.new_dataset:
        out["$new_dataset"] = list(node.new_dataset)
    if node.always_follow:
        out["$always_follow"] = list(node.always_follow)
    if node.reset_external_values:
        out["$reset_external_values"] = [
            {"external_dataset": r.external_dataset, "field": r.field}
            for r in node.reset_external_values
        ]
    for child in node.children:
        out[child.name] = _node_value(child)
    if node.external_values:
        out["$external_values"] = [
            {
                "external_dataset": e.external_dataset,
                "field": e.field,
                "dataset": e.dataset,
            }
            | ({"name": e.name} if e.name is not None else {})
            for e in node.external_values
        ]
    if node.dataset_processing:
        out["$dataset_processing"] = [
            {"process": d.process, "dataset": d.dataset}
            for d in node.dataset_processing
        ]
    return out


def profile_to_dict(profile: Profile) -> dict[str, Any]:
    """Return ``profile`` as a plain mapping, ready for YAML or JSON."""
    return {root.name: _node_value(root) for root in profile.roots}


def load_yaml(text: str | bytes) -> Any:
    import yaml  # imported on first use to keep `import xmldataset` fast

    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        column = mark.column + 1 if mark is not None else None
        raise ProfileError(f"invalid YAML: {exc}", line=line, column=column) from None


def dump_yaml(data: Mapping[str, Any]) -> str:
    import yaml

    text: str = yaml.safe_dump(dict(data), sort_keys=False, allow_unicode=True)
    return text


def load_profile(path: str | PathLike[str]) -> Profile:
    """Load a profile from a file, choosing the format from its extension.

    ``.yaml``/``.yml`` files are read as YAML,
    ``.json`` files as JSON, and anything else as the indented text syntax.

    Raises:
        ProfileError: The profile is invalid.
        OSError: The file cannot be read.
    """
    file = Path(path)
    suffix = file.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return profile_from_dict(load_yaml(file.read_bytes()))
    if suffix == ".json":
        try:
            data = json.loads(file.read_bytes())
        except json.JSONDecodeError as exc:
            raise ProfileError(
                f"invalid JSON: {exc.msg}", line=exc.lineno, column=exc.colno
            ) from None
        return profile_from_dict(data)
    return parse_dsl(file.read_text(encoding="utf-8"))
