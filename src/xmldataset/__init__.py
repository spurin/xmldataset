"""Extract Python datasets from XML using a simple, indented profile.

A profile mirrors the structure of the XML and says which elements and
attributes go into which datasets. Profiles can be written in the indented text
syntax, in YAML, or in JSON; all three compile to the same :class:`Profile`.
"""

import importlib.metadata

from ._api import (
    Record,
    XMLSource,
    compile_profile,
    iter_records,
    json_schema,
    load_profile,
    parse_using_profile,
)
from ._errors import (
    ConfigurationError,
    MissingProcessError,
    ProfileError,
    XMLDatasetError,
)
from ._model import DatasetProcess, ExternalReset, ExternalValue, Field, Node, Profile

__all__ = [
    "ConfigurationError",
    "DatasetProcess",
    "ExternalReset",
    "ExternalValue",
    "Field",
    "MissingProcessError",
    "Node",
    "Profile",
    "ProfileError",
    "Record",
    "XMLDatasetError",
    "XMLSource",
    "compile_profile",
    "iter_records",
    "json_schema",
    "load_profile",
    "parse_using_profile",
]

# Public classes report the package they are imported from, so tracebacks and
# reprs say xmldataset.ProfileError rather than naming a private module.
for _public in (
    ConfigurationError,
    DatasetProcess,
    ExternalReset,
    ExternalValue,
    Field,
    MissingProcessError,
    Node,
    Profile,
    ProfileError,
    XMLDatasetError,
):
    _public.__module__ = __name__
del _public

__author__ = "James Spurin"
__email__ = "james@spurin.com"

try:
    __version__ = importlib.metadata.version("xmldataset")
except importlib.metadata.PackageNotFoundError:  # source tree, not installed
    __version__ = "0+unknown"
