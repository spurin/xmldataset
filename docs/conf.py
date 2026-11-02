"""Sphinx configuration for the xmldataset documentation."""

from datetime import date
from importlib.metadata import version as package_version

project = "xmldataset"
author = "James Spurin"
copyright = f"2014-{date.today().year}, {author}"
release = package_version("xmldataset")
version = ".".join(release.split(".")[:2])

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build"]

html_theme = "furo"
html_title = "xmldataset"
html_logo = "_shared_static/logo.jpg"
html_static_path = ["_shared_static"]
html_theme_options = {
    "source_repository": "https://github.com/spurin/xmldataset/",
    "source_branch": "master",
    "source_directory": "docs/",
}
