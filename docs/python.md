# Using xmldataset from Python

## Parsing

{func}`~xmldataset.parse_using_profile` reads the XML and returns every dataset
as a list of records:

```pycon
>>> import xmldataset
>>> xml = """
... <library>
...     <book id="1"><title>Dune</title><author>Frank Herbert</author></book>
...     <book id="2"><title>Emma</title></book>
... </library>"""
>>> profile = """
... library
...     book
...         id     = dataset:books
...         title  = dataset:books
...         author = dataset:books
... """
>>> xmldataset.parse_using_profile(xml, profile)
{'books': [{'id': '1', 'title': 'Dune', 'author': 'Frank Herbert'}, {'id': '2', 'title': 'Emma'}]}
```

The XML can be:

- a `str` or `bytes` of XML content (a `str` is never treated as a file name);
- a path, as a {class}`pathlib.Path` or other {class}`os.PathLike`;
- an open file, preferably in binary mode;
- an already parsed {class}`xml.etree.ElementTree.Element` or `ElementTree`,
  which is left untouched.

The profile can be text, a YAML/JSON-style mapping, or a {class}`~xmldataset.Profile`
from {func}`~xmldataset.compile_profile` or {func}`~xmldataset.load_profile`.
Compiling once is worthwhile when you parse many documents with one profile:

```python
profile = xmldataset.load_profile("books.yaml")
for path in Path("incoming").glob("*.xml"):
    save(xmldataset.parse_using_profile(path, profile))
```

## Streaming

{func}`~xmldataset.iter_records` yields `(dataset, record)` pairs as soon as each
record is complete. The document is read incrementally and discarded as it goes,
so memory stays flat however large the file is:

```pycon
>>> for dataset, record in xmldataset.iter_records(xml, profile):
...     print(dataset, record)
books {'id': '1', 'title': 'Dune', 'author': 'Frank Herbert'}
books {'id': '2', 'title': 'Emma'}
```

Pass a `Path` or a binary file so the XML text itself is never held in memory.
A record is only held back while a later part of the document could still add to
it; see [Streaming and memory](profiles.md#streaming-and-memory).

## Process functions

`process:` on a field names a function that transforms the value. Supply the
functions as a mapping:

```pycon
>>> profile = """
... library
...     book
...         title = dataset:books,process:shout
... """
>>> xmldataset.parse_using_profile(xml, profile, process={"shout": str.upper})
{'books': [{'title': 'DUNE'}, {'title': 'EMMA'}]}
```

`__DATASET_PROCESSING__ = FUNCTION:DATASET` passes the dataset's current record to
a function when an element ends, to add or change fields in place:

```pycon
>>> def count_words(record):
...     record["words"] = len(record["title"].split())
>>> profile = """
... library
...     book
...         title = dataset:books
...         __DATASET_PROCESSING__ = count_words:books
... """
>>> xmldataset.parse_using_profile(xml, profile, process={"count_words": count_words})
{'books': [{'title': 'Dune', 'words': 1}, {'title': 'Emma', 'words': 1}]}
```

Every function a profile names must be supplied, or a
{class}`~xmldataset.MissingProcessError` is raised before any XML is read.

## Global values

`global_values` are added to the start of every record:

```pycon
>>> profile = "library\n    book\n        title = dataset:books"
>>> xmldataset.parse_using_profile(xml, profile, global_values={"source": "library.xml"})
{'books': [{'source': 'library.xml', 'title': 'Dune'}, {'source': 'library.xml', 'title': 'Emma'}]}
```

## Dispatching batches

`dispatch` hands records to a function in batches instead of returning them, for
example to write each batch to a database while the document is still being
read. Each callback receives `{dataset: [records]}`:

```pycon
>>> batches = []
>>> xmldataset.parse_using_profile(
...     xml, profile, dispatch={"books": {"counter": 1, "coderef": batches.append}}
... )
{}
>>> batches
[{'books': [{'title': 'Dune'}]}, {'books': [{'title': 'Emma'}]}]
```

- Key the settings by dataset name, or use `"__generic__"` for every dataset.
  Per-dataset settings fall back to `"__generic__"` for anything they leave out.
- `counter` is the batch size; the last batch may be smaller.
- Datasets without a `coderef` are returned as usual.

{func}`~xmldataset.iter_records` is often simpler: batch records with
{func}`itertools.batched` or send them wherever you like.

## Namespaces

Plain names in a profile match elements and attributes by local name in any
namespace, which is usually all you need:

```pycon
>>> atom = """
... <feed xmlns="http://www.w3.org/2005/Atom">
...     <entry><title>First post</title></entry>
... </feed>"""
>>> xmldataset.parse_using_profile(atom, "feed\n  entry\n    title = dataset:posts")
{'posts': [{'title': 'First post'}]}
```

To match one namespace exactly, use `prefix:name` in the profile and map the
prefixes with `namespaces` (Clark notation, `{uri}name`, also works):

```{include} _generated/examples/namespaces/profile.md
```

```python
namespaces = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
}
result = xmldataset.parse_using_profile(xml, profile, namespaces=namespaces)
```

```{include} _generated/examples/namespaces/output.md
```

The `xml:` prefix (as in `xml:lang`) is always available.

## Errors

All errors raised by xmldataset derive from {class}`~xmldataset.XMLDatasetError`.

- {class}`~xmldataset.ProfileError`: the profile is invalid. For text profiles
  `line` and `column` locate the problem; for YAML/JSON, `location` does.
- {class}`~xmldataset.MissingProcessError`: a process function is missing.
- {class}`~xmldataset.ConfigurationError`: an option is invalid.

Malformed XML raises the standard library's
{class}`xml.etree.ElementTree.ParseError`.

```pycon
>>> xmldataset.compile_profile("library\n    book = datset:books")
Traceback (most recent call last):
  ...
xmldataset.ProfileError: line 2, column 12: unknown key 'datset' (did you mean 'dataset'?)
```

## pandas

Each dataset is a list of dicts, which pandas reads directly:

```python
import pandas as pd

result = xmldataset.parse_using_profile(xml, profile)
books = pd.DataFrame(result["books"])
```
