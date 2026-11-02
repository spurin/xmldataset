# Upgrading from 1.x

xmldataset 2.0 is a rewrite. Most profiles work unchanged, and for complete,
regular XML the output is the same. Where it differs, 1.x was usually putting
values in the wrong record. This page lists every change.

**Requirements:** Python 3.11 or newer.

## Output changes

### Records no longer mix values from different elements

In 1.x, when an element was missing, the next element's value could land in the
previous record. Here the second book has no author:

```{include} _generated/examples/missing-elements/input.md
```

::::{grid} 2
:::{grid-item}
**1.x** gives Emma James Joyce's name:
```{include} _generated/examples/missing-elements/legacy.md
```
:::
:::{grid-item}
**2.0:**
```{include} _generated/examples/missing-elements/output.md
```
:::
::::

### Values from enclosing elements reach every record inside them

A field declared on an enclosing element, such as a shop's `number` attribute,
is now copied into every record inside it. In 1.x it went into one record, which
could belong to a different shop (see the [Quickstart](quickstart.md#values-from-an-enclosing-element)):

::::{grid} 2
:::{grid-item}
**1.x:**
```{include} _generated/examples/shop-number/legacy.md
```
:::
:::{grid-item}
**2.0:**
```{include} _generated/examples/shop-number/output.md
```
:::
::::

This works even when the enclosing value appears after the records (see
[How records are built](profiles.md#how-records-are-built)).

### Other output changes

- **No empty records.** 1.x could emit `{}` for an element with `__NEW_DATASET__`
  that had nothing to capture.
- **Two occurrences of the same child element no longer share a record.** If
  values from several `<info>` blocks inside one `<book>` should combine, add
  `__NEW_DATASET__` on `book` (see [Choosing the record element](profiles.md#choosing-the-record-element)).
- **An element's text and its attributes can be captured together** with a
  field line that opens a block (issue #13). 1.x dropped the attributes.
- **Namespaced XML matches by local name.** A profile with plain names returned
  `{}` for namespaced XML in 1.x. Field names come from the profile, not from
  the `{uri}tag` form.
- **External values are scoped** to the element enclosing their source and the
  element that uses them, so a shop without a number no longer inherits the
  previous shop's. A value that never appears leaves the field out; 1.x could
  write an empty string.
- **`global_values` are added to every record.** 1.x skipped records started by
  `__NEW_DATASET__` or by an external value.
- **Values pair up in document order.** `<name>A</name><value>1</value><name>B</name><value>2</value>`
  gives `{name: A, value: 1}, {name: B, value: 2}`.
- **An unindented field line works**, for example `catalog = dataset:d` to capture
  the root element's text. 1.x misread it.
- **Key order within a record can differ** from 1.x. Records compare equal
  regardless of key order.

## Stricter profiles

Profile mistakes that 1.x silently ignored or misread are now errors, reported as
{class}`~xmldataset.ProfileError` with a line and column:

- unknown modifiers such as `datset:` and unknown directives such as
  `__NEW_DATASETS__`;
- directives that name a dataset or external value that nothing in the profile
  produces, such as `__NEW_DATASET__ = d1,d2` (a comma instead of a space);
- a name that is both ignored (`__IGNORE__`) and captured;
- fields with neither `dataset:` nor `external_dataset:`;
- indentation that does not line up with an outer level, indentation under a
  line that cannot contain anything, and mixed tabs and spaces.

Things 1.x could not express now work:

- values with spaces or commas, quoted: `default:"not rated"`;
- values with colons or equals signs: `default:12:30`;
- `#` comment lines;
- the same name more than once in a block: the definitions merge. In 1.x, a later
  block replaced an earlier field with the same name.

## Python API changes

- **Options are explicit keyword arguments.** A misspelt option such as
  `global_value=` now raises `TypeError`; 1.x ignored it.
- **`dispatch` returns a dict** of the datasets that had no dispatcher (`{}` when
  every dataset was dispatched) instead of `None`. A dataset without a dispatcher
  is returned rather than crashing, and per-dataset settings fall back to
  `"__generic__"` for anything they leave out.
- **Process functions are checked before parsing.** A profile that names a
  function you did not supply raises {class}`~xmldataset.MissingProcessError`,
  even if the field never appears in the XML. The messages are unchanged.
- **Errors are typed.** {class}`~xmldataset.ProfileError` and
  {class}`~xmldataset.ConfigurationError` subclass `ValueError`, and
  {class}`~xmldataset.MissingProcessError` subclasses `LookupError`; all derive
  from {class}`~xmldataset.XMLDatasetError`. 1.x raised bare `Exception`.
- **A string that names an existing file is rejected** with a hint to pass a
  `pathlib.Path`, since a `str` is always read as XML content.
- **`python -m xmldataset` is now the [command-line tool](cli.md)**; the
  built-in demo is gone.
- The private `_XMLDataset` class is gone, and xmldataset no longer changes the
  level of a logger called `"default"`.

## New in 2.0

YAML and JSON profiles, {func}`~xmldataset.iter_records` for streaming,
{func}`~xmldataset.compile_profile` and {func}`~xmldataset.load_profile`,
`list:true`, the `namespaces` option, path and file inputs, and the
[command line](cli.md). See the [changelog](changelog.md) for the full list.
