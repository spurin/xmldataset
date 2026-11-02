# xmldataset: simple XML parsing 🗃️

[![CI](https://github.com/spurin/xmldataset/actions/workflows/ci.yml/badge.svg)](https://github.com/spurin/xmldataset/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/xmldataset)](https://pypi.org/project/xmldataset/)
[![Python versions](https://img.shields.io/pypi/pyversions/xmldataset)](https://pypi.org/project/xmldataset/)
[![Documentation](https://readthedocs.org/projects/xmldataset/badge/?version=latest)](https://xmldataset.readthedocs.io)

![xmldataset logo](https://xmldataset.readthedocs.io/en/latest/_static/logo.jpg)

A Python library that simplifies the extraction of datasets from XML content.

XML is a simple markup format. Whilst simple, extracting data of interest is often more
complicated than it needs to be.

xmldataset addresses this through an easy to use plaintext declaration (a *profile*) that
follows the structure of the XML document. The profile is indented, matching the XML
structure, and the data we are interested in is tagged against a dataset.

- Documentation: <https://xmldataset.readthedocs.io>
- Source: <https://github.com/spurin/xmldataset>

## Installation

```console
pip install xmldataset
```

xmldataset requires Python 3.11 or newer and has no dependencies.

## Example

```python
import xmldataset

xml = """<?xml version="1.0"?>
<colleagues>
    <colleague>
        <title>The Boss</title>
        <phone>+1 202-663-9108</phone>
        <email>boss@the_company.com</email>
    </colleague>
    <colleague>
        <title>Admin Assistant</title>
        <phone>+1 347-999-5454</phone>
        <email>admin@the_company.com</email>
    </colleague>
</colleagues>"""

profile = """
colleagues
    colleague
        title = dataset:colleagues
        phone = dataset:colleagues
        email = dataset:colleagues"""

print(xmldataset.parse_using_profile(xml, profile))
```

```text
{'colleagues': [{'title': 'The Boss', 'phone': '+1 202-663-9108', 'email': 'boss@the_company.com'}, {'title': 'Admin Assistant', 'phone': '+1 347-999-5454', 'email': 'admin@the_company.com'}]}
```

## Features

- Handles missing data from the XML structure: if it's missing in the XML, it is not
  populated in the dataset
- Handles both XML elements and attributes using the plaintext profile (attributes are
  depicted as a sublevel of an element)
- Easy to rename XML attributes and elements during processing to meet your requirements
- Inline manipulation of XML content through the process mechanism
- Dispatch mechanism, allowing datasets to be dispatched for every N instances to enable
  asynchronous processing

## Contributing

See [CONTRIBUTING.md](https://github.com/spurin/xmldataset/blob/master/CONTRIBUTING.md). Changes are recorded in
[CHANGELOG.md](https://github.com/spurin/xmldataset/blob/master/CHANGELOG.md).

## License

BSD-3-Clause. See [LICENSE](https://github.com/spurin/xmldataset/blob/master/LICENSE).
