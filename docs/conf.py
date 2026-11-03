"""Sphinx configuration for the xmldataset documentation."""

import sys
from datetime import date
from importlib.metadata import version as package_version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_ext"))
# Filled by the xmldataset_examples extension; must exist before Sphinx checks it.
(Path(__file__).parent / "_generated" / "extra").mkdir(parents=True, exist_ok=True)

project = "xmldataset"
author = "James Spurin"
copyright = f"2014-{date.today().year}, {author}"
release = package_version("xmldataset")
version = ".".join(release.split(".")[:2])

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "xmldataset_examples",
]
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "_generated"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_type_aliases = {
    "XMLSource": "xmldataset.XMLSource",
    "Record": "xmldataset.Record",
}
napoleon_google_docstring = True
napoleon_numpy_docstring = False

html_theme = "furo"
html_title = f"xmldataset {release}"
html_logo = "_static/logo.jpg"
html_static_path = ["_static"]
# Published at /<version>/schema/profile-v1.json for editors (see formats.md).
html_extra_path = ["_generated/extra"]
html_theme_options = {
    "source_repository": "https://github.com/spurin/xmldataset/",
    "source_branch": "main",
    "source_directory": "docs/",
}
