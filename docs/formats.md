# Choosing a format

Every profile can be written as indented **text**, as **YAML**, or as **JSON**.
All three compile to the same profile and produce identical results, and you can
convert between them at any time.

| | Text | YAML | JSON |
| --- | --- | --- | --- |
| Best for | Writing by hand; the most compact | Teams that already use YAML for configuration | Profiles generated or stored by other programs |
| Comments | `#` lines | `#` lines | No |
| Editor completion | No | Yes, with the JSON Schema | Yes, with the JSON Schema |
| File extension | anything else, e.g. `.txt` | `.yaml` or `.yml` | `.json` |

Here is the same profile in each format:

```{include} _generated/examples/parent-values/profile.md
```

## Loading and passing profiles

```python
import xmldataset

profile = xmldataset.load_profile("books.yaml")  # format chosen by extension
result = xmldataset.parse_using_profile(xml, profile)
```

`parse_using_profile`, `iter_records` and `compile_profile` also accept a profile
directly: a string is read as text syntax, and a mapping (for example the result
of `yaml.safe_load` or `json.load`) as YAML/JSON structure.

## Converting

From the command line:

```console
xmldataset convert books.txt --to yaml -o books.yaml
xmldataset convert books.yaml --to json
xmldataset convert books.json --to dsl
```

From Python, every compiled profile can write itself out:

```pycon
>>> import xmldataset
>>> profile = xmldataset.compile_profile("""
... library
...     book
...         title  = dataset:books
...         rating = dataset:books,default:"not rated"
... """)
>>> print(profile.to_yaml(), end="")
library:
  book:
    title: books
    rating:
      $dataset: books
      $default: not rated
>>> print(profile.to_json(), end="")
{
  "library": {
    "book": {
      "title": "books",
      "rating": {
        "$dataset": "books",
        "$default": "not rated"
      }
    }
  }
}
>>> print(profile.to_dsl(), end="")
library
    book
        title = dataset:books
        rating = dataset:books,default:"not rated"
```

Conversion is lossless, so converting back gives an identical profile. Comments
in text and YAML profiles are not carried over.

## Editor support

YAML and JSON profiles have a [JSON Schema](https://json-schema.org/), published
at:

```text
https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json
```

It gives completion, hover help and validation in editors that support JSON
Schema, including VS Code (with the YAML extension for YAML files), JetBrains
IDEs and Neovim.

In **JSON**, point to it with a `$schema` key, which xmldataset ignores:

```json
{
  "$schema": "https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json",
  "library": {"book": {"title": "books"}}
}
```

In **YAML**, add a modeline comment at the top of the file:

```yaml
# yaml-language-server: $schema=https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json
library:
  book:
    title: books
```

The schema is also available offline: `xmldataset schema` prints it, and
`xmldataset.json_schema()` returns it.

## YAML pitfalls

YAML turns some unquoted words into other types. xmldataset reads unquoted
whole numbers (such as a dataset called `1`) as text, and rejects anything else
that is not a string. Quote these:

- `yes`, `no`, `on`, `off`, `true`, `false`, `y` and `n`, which YAML reads as
  booleans. This applies to keys too, so an element called `on` must be written
  `"on":`.
- Numbers with a decimal point, such as `default: "1.10"` (YAML would read
  `1.1`).
- Values that start with a special character such as `*`, `&`, `!`, `%`, `@`, or
  a backtick.
