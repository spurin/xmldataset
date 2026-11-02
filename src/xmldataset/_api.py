"""Public functions."""

from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator, Mapping
from functools import lru_cache
from importlib.resources import files
from typing import IO, Any, TypeAlias

from ._dsl import parse_dsl
from ._engine import Engine, compile_runtime, iter_events
from ._errors import ConfigurationError
from ._model import Profile
from ._structured import load_profile, profile_from_dict

__all__ = [
    "Record",
    "XMLSource",
    "compile_profile",
    "iter_records",
    "json_schema",
    "load_profile",
    "parse_using_profile",
]

Record: TypeAlias = dict[str, Any]
"""One row of a dataset: field name to value."""

XMLSource: TypeAlias = (
    str
    | bytes
    | bytearray
    | memoryview
    | os.PathLike[str]
    | IO[bytes]
    | IO[str]
    | ET.Element
    | ET.ElementTree
)
"""XML to read: ``str``/``bytes`` content, a path, a file object, or an element."""

ProfileSource: TypeAlias = str | Mapping[str, Any] | Profile
"""A profile: text syntax (``str``), a YAML/JSON mapping, or a :class:`Profile`."""


@lru_cache(maxsize=128)
def _from_text(text: str) -> Profile:
    return parse_dsl(text)


def compile_profile(profile: ProfileSource) -> Profile:
    """Compile a profile once so it can be reused for many documents.

    Every parsing function accepts the same inputs and calls this for you; use
    it directly to validate a profile up front or to convert between formats.

    Args:
        profile: A profile in the indented text syntax (``str``), a mapping in
            the YAML/JSON structure (for example the result of
            ``yaml.safe_load``), or an existing :class:`Profile`.

    Returns:
        The compiled, immutable profile.

    Raises:
        ProfileError: The profile is invalid. For the text syntax, ``line`` and
            ``column`` locate the problem.

    Example:
        >>> profile = compile_profile('''
        ... catalog
        ...     book
        ...         title = dataset:books''')
        >>> print(profile.to_json(), end="")
        {
          "catalog": {
            "book": {
              "title": "books"
            }
          }
        }
    """
    if isinstance(profile, Profile):
        return profile
    if isinstance(profile, str):
        return _from_text(profile)
    if isinstance(profile, Mapping):
        return profile_from_dict(profile)
    raise TypeError(
        f"profile must be str, a mapping, or a Profile, not {type(profile).__name__}"
    )


def iter_records(
    xml: XMLSource,
    profile: ProfileSource,
    *,
    process: Mapping[str, Callable[[Any], Any]] | None = None,
    global_values: Mapping[str, Any] | None = None,
    namespaces: Mapping[str, str] | None = None,
) -> Iterator[tuple[str, Record]]:
    """Stream records from XML as soon as each one is complete.

    The document is read incrementally and each element is discarded once it
    has been processed, so memory use stays flat for large files. Pass a path or
    a binary file object to avoid holding the XML text in memory at all.

    Records of the same dataset are yielded in document order. A record is held
    back only while a value for it may still appear later in the document (see
    "Forward references" in the profile documentation).

    Args:
        xml: The XML: content as ``str`` or ``bytes``, an :class:`os.PathLike`
            path, a file object, or an :class:`~xml.etree.ElementTree.Element`.
            A ``str`` is always treated as XML content, never as a file name.
        profile: The profile; see :func:`compile_profile`.
        process: Functions referred to by ``process:`` and
            ``__DATASET_PROCESSING__`` in the profile, by name.
        global_values: Values added to every record.
        namespaces: Namespace prefixes used in the profile, mapped to URIs, for
            example ``{"atom": "http://www.w3.org/2005/Atom"}``.

    Yields:
        ``(dataset, record)`` pairs.

    Raises:
        ProfileError: The profile is invalid.
        MissingProcessError: The profile names a process function that was not
            supplied. Raised before any XML is read.
        ConfigurationError: An option is invalid.
        xml.etree.ElementTree.ParseError: The XML is malformed. Records before
            the error have already been yielded.

    Example:
        >>> xml = "<shop><book>Dune</book><book>Emma</book></shop>"
        >>> for dataset, record in iter_records(xml, "shop\\n  book = dataset:books"):
        ...     print(dataset, record)
        books {'book': 'Dune'}
        books {'book': 'Emma'}
    """
    engine = Engine(
        compile_runtime(compile_profile(profile), namespaces), process, global_values
    )
    return iter_events(engine, xml)


def _dispatcher(
    dispatch: Mapping[str, Mapping[str, Any]] | None,
) -> Callable[[str], tuple[int, Callable[[dict[str, list[Record]]], object]] | None]:
    if dispatch is None:
        return lambda dataset: None
    if not isinstance(dispatch, Mapping):
        raise ConfigurationError("dispatch must map dataset names to settings")
    for dataset, settings in dispatch.items():
        if not isinstance(settings, Mapping):
            raise ConfigurationError(f"dispatch[{dataset!r}] must be a mapping")
        unknown = set(settings) - {"counter", "coderef"}
        if unknown:
            raise ConfigurationError(
                f"dispatch[{dataset!r}] has unknown keys {sorted(unknown)};"
                " expected 'counter' and 'coderef'"
            )
        counter = settings.get("counter", 0)
        if isinstance(counter, bool) or not isinstance(counter, int) or counter < 0:
            raise ConfigurationError(
                f"dispatch[{dataset!r}]['counter'] must be an int >= 0"
            )
        if "coderef" in settings and not callable(settings["coderef"]):
            raise ConfigurationError(
                f"dispatch[{dataset!r}]['coderef'] must be callable"
            )
    generic = dispatch.get("__generic__", {})

    def route(
        dataset: str,
    ) -> tuple[int, Callable[[dict[str, list[Record]]], object]] | None:
        settings = dispatch.get(dataset, {})
        coderef = settings.get("coderef", generic.get("coderef"))
        if coderef is None:
            return None
        counter = settings.get("counter", generic.get("counter", 0))
        return max(counter, 1), coderef

    return route


def parse_using_profile(
    xml: XMLSource,
    profile: ProfileSource,
    *,
    process: Mapping[str, Callable[[Any], Any]] | None = None,
    dispatch: Mapping[str, Mapping[str, Any]] | None = None,
    global_values: Mapping[str, Any] | None = None,
    namespaces: Mapping[str, str] | None = None,
) -> dict[str, list[Record]]:
    """Extract datasets from XML.

    Args:
        xml: The XML; see :func:`iter_records` for the accepted types.
        profile: The profile; see :func:`compile_profile`.
        process: Functions referred to by ``process:`` and
            ``__DATASET_PROCESSING__`` in the profile, by name.
        dispatch: Hand records to callbacks in batches instead of returning
            them. Keys are dataset names, or ``"__generic__"`` for every
            dataset; values are ``{"counter": n, "coderef": function}``. Each
            callback receives ``{dataset: [record, ...]}`` with ``n`` records
            (fewer for the last batch). Datasets without a callback are returned
            as usual.
        global_values: Values added to every record.
        namespaces: Namespace prefixes used in the profile, mapped to URIs.

    Returns:
        Each dataset name mapped to its records, in document order. Datasets
        handed to ``dispatch`` callbacks are not included.

    Raises:
        ProfileError: The profile is invalid.
        MissingProcessError: The profile names a process function that was not
            supplied.
        ConfigurationError: An option is invalid.
        xml.etree.ElementTree.ParseError: The XML is malformed.

    Example:
        >>> xml = '''
        ... <colleagues>
        ...   <colleague><title>Boss</title><email>b@example.com</email></colleague>
        ...   <colleague><title>Minion</title></colleague>
        ... </colleagues>'''
        >>> parse_using_profile(xml, '''
        ... colleagues
        ...     colleague
        ...         title = dataset:people
        ...         email = dataset:people''')
        {'people': [{'title': 'Boss', 'email': 'b@example.com'}, {'title': 'Minion'}]}
    """
    route = _dispatcher(dispatch)
    engine = Engine(
        compile_runtime(compile_profile(profile), namespaces), process, global_values
    )
    result: dict[str, list[Record]] = {}
    batches: dict[str, list[Record]] = {}
    for dataset, record in iter_events(engine, xml):
        target = route(dataset)
        if target is None:
            result.setdefault(dataset, []).append(record)
            continue
        size, callback = target
        batch = batches.setdefault(dataset, [])
        batch.append(record)
        if len(batch) >= size:
            callback({dataset: batch})
            batches[dataset] = []
    for dataset, batch in batches.items():
        target = route(dataset)
        if batch and target is not None:
            target[1]({dataset: batch})
    return {dataset: result[dataset] for dataset in engine.order if dataset in result}


def json_schema() -> dict[str, Any]:
    """Return the JSON Schema for YAML/JSON profiles.

    The same schema is published at
    https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json for
    editor completion and validation.
    """
    text = (
        files("xmldataset")
        .joinpath("profile-v1.schema.json")
        .read_text(encoding="utf-8")
    )
    schema: dict[str, Any] = json.loads(text)
    return schema
