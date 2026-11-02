# xmldataset: simple XML parsing 🗃️

[![CI](https://github.com/spurin/xmldataset/actions/workflows/ci.yml/badge.svg)](https://github.com/spurin/xmldataset/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/xmldataset)](https://pypi.org/project/xmldataset/)
[![Python versions](https://img.shields.io/pypi/pyversions/xmldataset)](https://pypi.org/project/xmldataset/)
[![Documentation](https://readthedocs.org/projects/xmldataset/badge/?version=latest)](https://xmldataset.readthedocs.io)

![xmldataset logo](https://xmldataset.readthedocs.io/en/latest/_static/logo.jpg)

**Extract Python datasets from XML with a simple profile that mirrors the XML.**

A *profile* lists the elements and attributes you want, indented the same way as
the XML, and names the *dataset* each value belongs to. xmldataset returns every
dataset as a list of records (plain dicts), ready for JSON, CSV, pandas or a
database.

**Profiles can be written as indented text, YAML or JSON.** All three are
equivalent, and you can convert between them at any time.

- Documentation: <https://xmldataset.readthedocs.io>
- Upgrading from 1.x: <https://xmldataset.readthedocs.io/en/stable/migration.html>

## Installation

```console
pip install xmldataset            # text and JSON profiles
pip install "xmldataset[yaml]"    # adds YAML profiles
```

xmldataset requires Python 3.11 or newer and has no other dependencies.

## Example

```pycon
>>> import xmldataset
>>> xml = """
... <colleagues>
...     <colleague><title>The Boss</title><email>boss@example.com</email></colleague>
...     <colleague><title>Minion</title></colleague>
... </colleagues>"""
>>> profile = """
... colleagues
...     colleague
...         title = dataset:colleagues
...         email = dataset:colleagues,default:none
... """
>>> result = xmldataset.parse_using_profile(xml, profile)
>>> for record in result["colleagues"]:
...     print(record)
{'title': 'The Boss', 'email': 'boss@example.com'}
{'title': 'Minion', 'email': 'none'}
```

<details>
<summary>The same profile in YAML</summary>

```yaml
colleagues:
  colleague:
    title: colleagues
    email:
      $dataset: colleagues
      $default: none
```

</details>

<details>
<summary>The same profile in JSON</summary>

```json
{
  "colleagues": {
    "colleague": {
      "title": "colleagues",
      "email": {
        "$dataset": "colleagues",
        "$default": "none"
      }
    }
  }
}
```

</details>

Load a profile file in any format with `xmldataset.load_profile("profile.yaml")`,
or stream records from a large file in flat memory:

```python
from pathlib import Path

for dataset, record in xmldataset.iter_records(Path("huge.xml"), profile):
    ...
```

Or skip Python entirely:

```console
xmldataset run profile.yaml data.xml --format csv --dataset colleagues
xmldataset convert profile.txt --to yaml
```

## Features

- **Three profile formats**: indented text, YAML or JSON, with a JSON Schema for
  editor completion and validation.
- **Elements and attributes**, with renaming, prefixes, defaults, lists of
  repeated values and per-value process functions.
- **Correct records by construction**: a record never mixes values from two
  elements, and values from an enclosing element (a shop's number, say) are
  copied into every record inside it.
- **Streams documents of any size** in flat memory from a string, bytes, a path
  or a file, and hands over each record as soon as it is complete.
- **Namespaces**, matched by local name or by prefix.
- **A command-line tool** to run, convert and validate profiles.
- **Typed, with no dependencies**; YAML support is an optional extra.

## Contributing

See [CONTRIBUTING.md](https://github.com/spurin/xmldataset/blob/master/CONTRIBUTING.md).
Changes are recorded in
[CHANGELOG.md](https://github.com/spurin/xmldataset/blob/master/CHANGELOG.md).

## License

BSD-3-Clause. See [LICENSE](https://github.com/spurin/xmldataset/blob/master/LICENSE).
