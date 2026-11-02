# Quickstart

This tutorial builds up a profile one feature at a time. Every example uses the
same XML, a catalogue of two bookshops:

:::{dropdown} The bookshop XML
:open:

```{include} _generated/examples/first-dataset/input.md
```
:::

Each example shows the profile in all three formats. Use whichever you prefer;
they give the same result. Run any of them like this:

```python
import xmldataset

result = xmldataset.parse_using_profile(xml, profile)
```

`xml` can be the XML as a string or bytes, a `pathlib.Path`, or an open file.
`profile` can be text, a YAML/JSON-style mapping, or a profile loaded with
`xmldataset.load_profile("profile.yaml")`.

## Your first dataset

The profile follows the XML down from the root: `catalog`, then `shop`, then
`book`. Inside `book`, two **fields** say that the text of `author` and `title`
goes into a dataset called `title_and_author`.

```{include} _generated/examples/first-dataset/profile.md
```

Every `<book>` becomes one record:

```{include} _generated/examples/first-dataset/output.md
```

In the text syntax, each line is an element name. A line with `=` is a field:
the value on the right says where its value goes. In YAML and JSON, a field whose
value only goes to one dataset can be written as just the dataset name.

## More than one dataset

A value can go to several datasets. List them separated by spaces in the text
syntax, or as a list in YAML and JSON:

```{include} _generated/examples/multiple-datasets/profile.md
```

```{include} _generated/examples/multiple-datasets/output.md
```

## Attributes

Attributes are written exactly like child elements: `id` below matches the `id`
attribute of `<book id="bk101">`.

```{include} _generated/examples/attributes/profile.md
```

```{include} _generated/examples/attributes/output.md
```

## Values from an enclosing element

The shop number is an attribute of `<shop>`, not of `<book>`. Declare it on the
shop and it is copied into every book record inside that shop. `name:` renames
the field from `number` to `shop`.

```{include} _generated/examples/shop-number/profile.md
```

```{include} _generated/examples/shop-number/output.md
```

This also works when the enclosing value comes *after* the records in the
document. See [How records are built](profiles.md#how-records-are-built).

## Renaming fields

`name:` changes the field name in the output. Here `genre` becomes `style`:

```{include} _generated/examples/rename-fields/profile.md
```

```{include} _generated/examples/rename-fields/output.md
```

## Prefixing field names

`prefix:` adds text to the front of the field name:

```{include} _generated/examples/prefix-fields/profile.md
```

```{include} _generated/examples/prefix-fields/output.md
```

## Processing values

`process:` names a Python function that transforms the value. Pass the functions
when you parse:

```python
result = xmldataset.parse_using_profile(xml, profile, process={"to_upper": str.upper})
```

```{include} _generated/examples/process-values/profile.md
```

```{include} _generated/examples/process-values/output.md
```

## Missing values and defaults

When an element is missing, its field is simply left out of that record. Use
`default:` to fill it in instead. Values containing spaces or commas are quoted
in the text syntax:

```{include} _generated/examples/defaults/input.md
```

```{include} _generated/examples/defaults/profile.md
```

```{include} _generated/examples/defaults/output.md
```

## Repeated elements as lists

By default, a field that appears again starts a new record. Add `list:true` to
collect the repeated values into a list instead:

```{include} _generated/examples/lists/input.md
```

```{include} _generated/examples/lists/profile.md
```

```{include} _generated/examples/lists/output.md
```

## Next steps

- [Profiles](profiles.md) covers every option and exactly how records are built.
- [Choosing a format](formats.md) compares text, YAML and JSON profiles and sets
  up editor completion.
- [Using xmldataset from Python](python.md) covers streaming, large files,
  dispatching batches, namespaces and errors.
- [The command line](cli.md) runs profiles without writing any Python.
