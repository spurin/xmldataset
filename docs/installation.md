# Installation

xmldataset needs Python 3.11 or newer and has no required dependencies.

```console
pip install xmldataset
```

To read profiles written in YAML, install the `yaml` extra, which adds
[PyYAML](https://pypi.org/project/PyYAML/):

```console
pip install "xmldataset[yaml]"
```

Text and JSON profiles need nothing extra. With [uv](https://docs.astral.sh/uv/),
use `uv add xmldataset` or `uv add "xmldataset[yaml]"`.

Installing the package also installs the [`xmldataset` command](cli.md).

Upgrading from 1.x? Read [Upgrading from 1.x](migration.md) first: some outputs
change, because several long-standing bugs are fixed.
