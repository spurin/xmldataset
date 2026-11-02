# xmldataset

**Extract Python datasets from XML with a simple profile that mirrors the XML.**

A *profile* lists the elements and attributes you want, indented the same way as
the XML, and names the *dataset* each value belongs to. xmldataset returns every
dataset as a list of records (plain dicts), ready for JSON, CSV, pandas or a
database.

:::{admonition} Text, YAML or JSON: your choice
:class: tip

Profiles can be written in **three equivalent formats**: an indented text syntax,
**YAML**, or **JSON**. Every example in this documentation shows all three. Pick
a tab and your choice follows you around the site. See
[Choosing a format](formats.md).
:::

## A first example

Given this XML:

```{include} _generated/examples/colleagues/input.md
```

this profile collects every colleague into a dataset called `colleagues`:

```{include} _generated/examples/colleagues/profile.md
```

```python
import xmldataset

result = xmldataset.parse_using_profile(xml, profile)
```

```{include} _generated/examples/colleagues/output.md
```

The Minion has no email address, so their record has no `email` field.

## Features

- **Three profile formats** that compile to the same thing: indented text, YAML
  or JSON, with a [JSON Schema](formats.md#editor-support) for editor completion.
- **Elements and attributes**, with renaming, prefixes, defaults, lists of
  repeated values and per-value [process functions](python.md#process-functions).
- **Correct records by construction.** A record never mixes values from two
  elements, and values from an enclosing element (a shop's number, say) are
  copied into every record inside it. See [How records are built](profiles.md#how-records-are-built).
- **Streams documents of any size** in flat memory, from a string, bytes, a path
  or a file; [`iter_records`](python.md#streaming) hands you each record as soon
  as it is complete.
- **Namespaces**, matched by local name or by prefix.
- **A command-line tool** to run profiles (JSON, JSON Lines or CSV output),
  convert them between formats, and validate them.
- **Typed, no dependencies.** YAML support is an optional extra.

```{toctree}
:hidden:
:caption: Guide

installation
quickstart
profiles
formats
python
cli
migration
```

```{toctree}
:hidden:
:caption: Reference

api
changelog
contributing
authors
```
