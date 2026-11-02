# The command line

Installing xmldataset adds an `xmldataset` command (also available as
`python -m xmldataset`). The profile format is chosen from the file extension:
`.yaml`/`.yml` for YAML, `.json` for JSON, and anything else for text.

## Run a profile

```console
xmldataset run books.yaml catalog.xml
```

prints every dataset as JSON. Options:

`-f`, `--format {json,jsonl,csv}`
: `json` (the default) prints all datasets at once. `jsonl` prints one line per
  record as it is produced, `{"dataset": ..., "record": {...}}`, so it streams
  large files in flat memory. `csv` prints one dataset as CSV, with a column for
  every field that appears.

`-d`, `--dataset NAME`
: Only output this dataset. Required for `csv` when the profile has several.

`-n`, `--namespace PREFIX=URI`
: A namespace prefix used in the profile. Repeat for several.

`-g`, `--global KEY=VALUE`
: A value added to every record. Repeat for several.

`-o`, `--output FILE`
: Write to a file instead of standard output.

Use `-` as the XML file to read standard input:

```console
curl -s https://example.com/feed.xml | xmldataset run feed.yaml - -n atom=http://www.w3.org/2005/Atom -f jsonl
```

Profiles that use `process:` or `__DATASET_PROCESSING__` need Python functions,
so they can only be run from Python.

## Convert a profile

```console
xmldataset convert books.txt --to yaml -o books.yaml
```

`--to` is `yaml` (the default), `json` or `dsl` (the text syntax).

## Validate profiles

```console
$ xmldataset validate books.yaml broken.txt
books.yaml: ok (books, titles)
broken.txt: line 3, column 16: unknown key 'datset' (did you mean 'dataset'?)
```

The exit status is 1 if any profile is invalid, which makes this suitable for CI
and pre-commit hooks.

## Print the JSON Schema

```console
xmldataset schema > profile-v1.json
```
