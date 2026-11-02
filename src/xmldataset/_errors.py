"""Exceptions raised by xmldataset."""

from __future__ import annotations

__all__ = [
    "ConfigurationError",
    "MissingProcessError",
    "ProfileError",
    "XMLDatasetError",
]


class XMLDatasetError(Exception):
    """Base class for every error raised by xmldataset.

    Malformed XML is reported by the standard library instead, as
    :class:`xml.etree.ElementTree.ParseError`.
    """


class ProfileError(XMLDatasetError, ValueError):
    """The profile is invalid.

    Attributes:
        message: Description of the problem, without location information.
        line: 1-based line number in a text profile, if known.
        column: 1-based column number in a text profile, if known.
        location: Where the problem is in a YAML/JSON/dict profile, for example
            ``catalog > book > $fields[1]``, if known.
    """

    def __init__(
        self,
        message: str,
        *,
        line: int | None = None,
        column: int | None = None,
        location: str | None = None,
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.location = location
        prefix = ""
        if line is not None:
            prefix = f"line {line}" + (f", column {column}" if column else "") + ": "
        elif location:
            prefix = f"{location}: "
        super().__init__(prefix + message)


class MissingProcessError(XMLDatasetError, LookupError):
    """The profile refers to a ``process`` function that was not supplied."""


class ConfigurationError(XMLDatasetError, ValueError):
    """An option passed to a parsing function is invalid."""
