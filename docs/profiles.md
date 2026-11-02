# Profiles

A profile is a tree of element names that mirrors the XML. Fields in the tree
say which values to capture and which dataset each one goes to. This page is the
complete reference; the [Quickstart](quickstart.md) is a gentler introduction.

## Matching elements and attributes

- The top-level names in a profile are candidates for the document's root
  element; whichever one matches is used.
- A name inside an element matches **child elements and attributes** with that
  name, so attributes need no special syntax.
- Anything the profile does not mention is skipped, along with everything
  inside it.
- A captured element's value is its text before the first child element, exactly
  as written (whitespace is kept). An empty element gives `None`. An attribute's
  value is the attribute text.
- A plain name such as `title` matches that local name in any namespace. Use
  `prefix:title` with the `namespaces` option, or `{uri}title`, to match one
  namespace exactly. See [Namespaces](python.md#namespaces).

## The text syntax

One entry per line. Indentation shows nesting; use spaces or tabs, but not both.
Blank lines and lines starting with `#` are ignored.

```text
# A comment
catalog                                  an element
    shop
        number = dataset:books,name:shop a field: number's value goes to books
        book
            __NEW_DATASET__ = books      a directive for <book>
            title  = dataset:books dataset:titles
            genre  = __IGNORE__          skip <genre> and everything inside it
```

A **field** line is `name = spec spec ...`. Each *spec* sends the value somewhere
and is a comma-separated list of `key:value` modifiers. A field line can also
have indented lines below it, to capture an element's text *and* its attributes
(see [below](#text-and-attributes-on-one-element)).

Values run to the next space or comma. Quote them with `"..."` or `'...'` when
they contain spaces or commas; inside quotes, `\"` and `\\` escape. Colons and
equals signs need no quoting: `default:12:30` and `default:a=b` work as written.

### Field modifiers

| Modifier | Meaning |
| --- | --- |
| `dataset:NAME` | Put the value in dataset `NAME`. |
| `external_dataset:NAME` | Hold the value in external dataset `NAME` for [`__EXTERNAL_VALUE__`](#external-values). |
| `name:FIELD` | Output field name. Defaults to the element or attribute name. |
| `prefix:TEXT` | Add `TEXT` to the front of the field name. |
| `process:FUNCTION` | Transform the value with a function passed in the `process` option. |
| `default:VALUE` | Use `VALUE` when the element or attribute is missing. `default:` alone gives `""`. |
| `list:true` | Collect repeated values into a list instead of starting a new record. |

Every spec needs `dataset:` or `external_dataset:` (or both).

### Directives

Directives are written inside the element they apply to.

| Directive | Meaning |
| --- | --- |
| `__NEW_DATASET__ = D1 D2` | This element is the [record boundary](#choosing-the-record-element) for datasets `D1` and `D2`. |
| `__EXTERNAL_VALUE__ = EXT:FIELD:D[:NAME]` | When this element ends, copy `FIELD` from external dataset `EXT` into dataset `D`, optionally renamed to `NAME`. |
| `__NEW_EXTERNAL_VALUE_HOLDER__ = EXT:FIELD` | When this element starts, forget the held value of `FIELD`. |
| `__DATASET_PROCESSING__ = FUNCTION:D` | When this element ends, call `FUNCTION(record)` on dataset `D`'s current record. |
| `__ALWAYS_FOLLOW__ = CHILD ...` | Apply the defaults inside `CHILD` even when `CHILD` is missing. |

### Errors

Mistakes are reported with the line and column, and a suggestion where one is
obvious. A directive that names a dataset or external value nothing in the
profile produces (usually a typo), and a name that is both ignored and
captured, are errors too.

```text
xmldataset.ProfileError: line 5, column 22: unknown key 'datset' (did you mean 'dataset'?)
```

## YAML and JSON profiles

The same tree as a mapping. Keys are element and attribute names; keys starting
with `$` are settings for the element they appear in. XML names cannot start
with `$`, so the two never clash.

An element or attribute's value can be:

- **a dataset name**: `title: books` sends the value to `books`;
- **a list of fields**: `title: [books, {dataset: titles, name: book_title}]`,
  where each item is a dataset name or a mapping of modifiers;
- **a mapping**: child elements and attributes, plus `$` settings;
- **nothing** (`null`): an element that only contains other elements.

| Setting | Text equivalent |
| --- | --- |
| `$dataset`, `$external_dataset`, `$name`, `$prefix`, `$process`, `$default`, `$list` | The element's own field, written `name = ...` |
| `$fields: [...]` | Several fields for the element's own value |
| `$ignore: true` | `name = __IGNORE__` |
| `$new_dataset: [D1, D2]` | `__NEW_DATASET__` |
| `$external_values: [{external_dataset, field, dataset, name}]` | `__EXTERNAL_VALUE__` |
| `$reset_external_values: [{external_dataset, field}]` | `__NEW_EXTERNAL_VALUE_HOLDER__` |
| `$dataset_processing: [{process, dataset}]` | `__DATASET_PROCESSING__` |
| `$always_follow: [CHILD]` | `__ALWAYS_FOLLOW__` |

Errors in YAML and JSON profiles name the location, for example
`catalog > book > title[1]: a field needs dataset or external_dataset`. See
[Choosing a format](formats.md) for editor support and YAML pitfalls.

## How records are built

Each dataset is a list of records. These rules decide which values share a
record:

1. **A value belongs to the element its field is written under.** `title` under
   `book` belongs to that `<book>`; an attribute belongs to its element. When a
   field's own element has a block of its own in the profile (attributes or
   children indented under it), its text belongs to that element, together with
   its attributes and children.
2. **A record never combines values from two occurrences of the same element.**
   A value from a new `<book>` starts a new record, even if the previous book
   was missing some of its fields.
3. **A field that the record already has starts a new record**, unless the field
   has `list:true`.
4. **Values from enclosing elements are copied into every record inside them**,
   meaning every record holding values from deeper inside that element, even
   when the enclosing value appears after those records in the document.
5. **Records are only created when a value is written**, so an element with
   nothing to capture produces no record. `global_values` are added to every
   record.

Values from *different* child elements of the same element combine into one
record (a `<header>` and a `<body>` inside one `<message>`, for example). A
record started by a repeated field (rule 3) only inherits values from enclosing
elements, not the other values of its own element; use `list:true` to keep
repeated values in one record.

Here the second book has no author. Its record is left without one; the third
book's author does not leak into it:

```{include} _generated/examples/missing-elements/input.md
```

```{include} _generated/examples/missing-elements/profile.md
```

```{include} _generated/examples/missing-elements/output.md
```

Here the shop's number and manager reach every book in that shop, although the
manager element comes after the books:

```{include} _generated/examples/parent-values/input.md
```

```{include} _generated/examples/parent-values/profile.md
```

```{include} _generated/examples/parent-values/output.md
```

### Choosing the record element

`__NEW_DATASET__` makes an element the record boundary for one or more datasets.
Every occurrence of that element (or of any other element with the same
directive) starts a new record, and elements *below* it no longer split records.
Use it when values from several occurrences of a child element should combine,
for example `<info>` blocks that each hold part of one book:

```text
catalog
    book
        __NEW_DATASET__ = books
        info
            author = dataset:books
            title  = dataset:books
```

With the bookshop XML from the [Quickstart](quickstart.md):

```{include} _generated/examples/new-dataset/profile.md
```

```{include} _generated/examples/new-dataset/output.md
```

### Text and attributes on one element

A field line can open a block for the element's attributes:

```{include} _generated/examples/text-and-attributes/input.md
```

```{include} _generated/examples/text-and-attributes/profile.md
```

```{include} _generated/examples/text-and-attributes/output.md
```

## External values

Rule 4 covers most cases where a value from one element belongs in records
built from another. External values handle the rest, such as a value from a
*sibling* element:

1. `external_dataset:NAME` on a field holds its value, under the field's name.
2. `__EXTERNAL_VALUE__ = NAME:FIELD:DATASET` copies the held value into
   `DATASET` when the element it is written in ends.

```{include} _generated/examples/external-values/profile.md
```

```{include} _generated/examples/external-values/output.md
```

A held value lasts as long as the element that encloses both the places it is
captured and the places it is used. With a shop-level number, a shop without
one therefore never inherits the previous shop's. If the same external field
is also captured somewhere outside the shops, its scope widens to cover all of
them, and the most recent value wins. If the value appears *later* in the document than
the records that use it, those records wait for it. If it never appears, the
field is left out. `__NEW_EXTERNAL_VALUE_HOLDER__` forgets a held value
explicitly when an element starts.

Names in `__EXTERNAL_VALUE__` cannot contain `:`. To use a prefixed attribute
such as `xl:href`, give it a plain name: `xl:href = external_dataset:links,name:href`,
then `__EXTERNAL_VALUE__ = links:href:items`.

## Defaults and `__ALWAYS_FOLLOW__`

`default:` applies when an element exists but has no child element or attribute
with the field's name. Defaults are not applied inside elements that are missing
altogether, unless the enclosing element lists them in `__ALWAYS_FOLLOW__`:

```text
book
    title = dataset:books
    __ALWAYS_FOLLOW__ = details
    details
        pages = dataset:books,default:unknown
```

A `<book>` without `<details>` still gets `pages: "unknown"`. If `details` also
captures its own text, its own default applies too. `__ALWAYS_FOLLOW__` can be
repeated at each level to reach deeper defaults.

## Processing a whole record

`__DATASET_PROCESSING__ = FUNCTION:DATASET` calls `FUNCTION(record)` on the
dataset's current record when the element ends; change the record in place. See
[Process functions](python.md#process-functions).

## Streaming and memory

xmldataset reads the document as a stream and hands each record over as soon as
nothing can change it. A record is held back only while a later part of the
document may still add to it:

- **A value from an enclosing element that has not appeared yet.** If a field is
  declared on an enclosing element and that element has not supplied it, every
  record inside the element is held until the value appears or the element
  ends. When the field is *missing*, the records are held until the element
  closes. For a field declared on the root element, that means the whole
  document, and [dispatch](python.md#dispatching-batches) callbacks only run at
  the end.
- **An external value that is used before it appears** (a forward reference).

To keep memory flat for very large documents, capture such values where they
appear before the records (attributes are always available first), or send them
to a separate dataset.
