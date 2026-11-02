"""The typed profile model shared by every profile format.

Text (DSL), YAML, JSON and plain-dict profiles are all compiled to a
:class:`Profile`; the parsing engine only ever sees this model.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from os import PathLike
from typing import Any

__all__ = [
    "DatasetProcess",
    "ExternalReset",
    "ExternalValue",
    "Field",
    "Node",
    "Profile",
]


@dataclass(frozen=True, slots=True)
class Field:
    """Where a captured value goes.

    A field captures the text of an element, or the value of an attribute, and
    stores it in a dataset, an external dataset, or both.

    Attributes:
        dataset: Name of the dataset that receives the value.
        external_dataset: Name of the external dataset that holds the value so
            that ``__EXTERNAL_VALUE__`` can copy it into other records.
        name: Output field name. Defaults to the element or attribute name.
        prefix: Text prepended to the output field name.
        process: Name of a function, supplied with the ``process`` option, that
            transforms the value.
        default: Value used when the element or attribute is missing.
            ``None`` means no default.
        as_list: Collect repeated values into a list instead of starting a new
            record (written ``list:true`` in a profile).
    """

    dataset: str | None = None
    external_dataset: str | None = None
    name: str | None = None
    prefix: str | None = None
    process: str | None = None
    default: str | None = None
    as_list: bool = False


@dataclass(frozen=True, slots=True)
class ExternalValue:
    """Copy a value held in an external dataset into a dataset's records.

    Written ``__EXTERNAL_VALUE__ = external_dataset:field:dataset[:name]``.
    """

    external_dataset: str
    field: str
    dataset: str
    name: str | None = None


@dataclass(frozen=True, slots=True)
class ExternalReset:
    """Forget a held external value when an element starts.

    Written ``__NEW_EXTERNAL_VALUE_HOLDER__ = external_dataset:field``.
    """

    external_dataset: str
    field: str


@dataclass(frozen=True, slots=True)
class DatasetProcess:
    """Call a function on a dataset's current record when an element ends.

    Written ``__DATASET_PROCESSING__ = process:dataset``.
    """

    process: str
    dataset: str


@dataclass(frozen=True, slots=True)
class Node:
    """An element (or attribute) in the profile tree.

    Attributes:
        name: Element or attribute name. ``prefix:local`` names are resolved
            with the ``namespaces`` option; ``{uri}local`` names match exactly;
            unprefixed names match the local name in any namespace.
        fields: Where this element's text (or this attribute's value) goes.
        children: Child elements and attributes, in profile order.
        ignore: Skip this element and everything inside it.
        new_dataset: Datasets whose records start at this element
            (``__NEW_DATASET__``).
        external_values: ``__EXTERNAL_VALUE__`` entries, applied when the
            element ends.
        reset_external_values: ``__NEW_EXTERNAL_VALUE_HOLDER__`` entries,
            applied when the element starts.
        dataset_processing: ``__DATASET_PROCESSING__`` entries, applied when
            the element ends.
        always_follow: Children whose defaults apply even when the child is
            missing (``__ALWAYS_FOLLOW__``).
    """

    name: str
    fields: tuple[Field, ...] = ()
    children: tuple[Node, ...] = ()
    ignore: bool = False
    new_dataset: tuple[str, ...] = ()
    external_values: tuple[ExternalValue, ...] = ()
    reset_external_values: tuple[ExternalReset, ...] = ()
    dataset_processing: tuple[DatasetProcess, ...] = ()
    always_follow: tuple[str, ...] = ()

    def child(self, name: str) -> Node | None:
        """Return the child called ``name``, or ``None``."""
        for node in self.children:
            if node.name == name:
                return node
        return None


@dataclass(frozen=True, slots=True)
class Profile:
    """A compiled profile: the tree of elements to extract from XML.

    Build one with :func:`xmldataset.compile_profile`,
    :func:`xmldataset.load_profile`, or the ``from_*`` constructors. Profiles
    are immutable and hashable, so one profile can be reused for many documents.

    Attributes:
        roots: The top-level elements. The one matching the XML document's root
            element is used.
    """

    roots: tuple[Node, ...]

    @classmethod
    def from_dsl(cls, text: str) -> Profile:
        """Compile a profile written in the indented text syntax."""
        from ._dsl import parse_dsl

        return parse_dsl(text)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Profile:
        """Compile a profile from a mapping, such as loaded YAML or JSON."""
        from ._structured import profile_from_dict

        return profile_from_dict(data)

    @classmethod
    def from_json(cls, text: str | bytes) -> Profile:
        """Compile a profile written as JSON."""
        import json

        return cls.from_dict(json.loads(text))

    @classmethod
    def from_yaml(cls, text: str | bytes) -> Profile:
        """Compile a profile written as YAML. Requires the ``yaml`` extra."""
        from ._structured import load_yaml

        return cls.from_dict(load_yaml(text))

    @classmethod
    def load(cls, path: str | PathLike[str]) -> Profile:
        """Load a profile file; see :func:`xmldataset.load_profile`."""
        from ._structured import load_profile

        return load_profile(path)

    def to_dsl(self) -> str:
        """Return the profile in the indented text syntax."""
        from ._dsl import profile_to_dsl

        return profile_to_dsl(self)

    def to_dict(self) -> dict[str, Any]:
        """Return the profile as a plain mapping, ready for YAML or JSON."""
        from ._structured import profile_to_dict

        return profile_to_dict(self)

    def to_json(self, *, indent: int | None = 2) -> str:
        """Return the profile as JSON."""
        import json

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False) + "\n"

    def to_yaml(self) -> str:
        """Return the profile as YAML. Requires the ``yaml`` extra."""
        from ._structured import dump_yaml

        return dump_yaml(self.to_dict())

    @property
    def datasets(self) -> tuple[str, ...]:
        """Names of the datasets the profile can produce, in profile order."""
        seen: dict[str, None] = {}

        def walk(node: Node) -> None:
            for spec in node.fields:
                if spec.dataset is not None:
                    seen.setdefault(spec.dataset)
            for ext in node.external_values:
                seen.setdefault(ext.dataset)
            for child in node.children:
                walk(child)

        for root in self.roots:
            walk(root)
        return tuple(seen)
