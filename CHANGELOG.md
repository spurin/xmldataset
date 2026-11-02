# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2.0.0 (unreleased)

A new engine, profile formats and tooling. Most profiles work unchanged.

### Added

- YAML and JSON profiles, equivalent to the text syntax, with a JSON Schema for
  editor completion (`xmldataset.json_schema()`, published on the docs site).
  PyYAML is a dependency, so YAML works without any extra install.
- `iter_records()`: stream `(dataset, record)` pairs as each record completes.
- `compile_profile()`, `load_profile()` and the `Profile` model, which converts
  between formats with `to_dsl()`, `to_yaml()`, `to_json()` and `to_dict()`.
- `list:true` collects repeated values into a list (issue #15).
- A field line can open a block, to capture an element's text and its
  attributes together (issue #13).
- Quoted values (`default:"not rated"`), and values containing `:` or `=`.
- `#` comment lines in text profiles.
- The `namespaces` option. Unprefixed names match the local name in any
  namespace.
- XML can be given as bytes, a path, a file object or a parsed `Element`.
- The `xmldataset` command: `run` (JSON, JSON Lines or CSV), `convert`,
  `validate` and `schema`.
- Typed exceptions: `XMLDatasetError`, `ProfileError` (with line and column),
  `MissingProcessError` and `ConfigurationError`.
- Type hints (`py.typed`).

### Changed

- The engine streams the document in document order, in bounded memory, with no
  limit on document depth.
- Values from enclosing elements are copied into every record inside them, even
  when they appear after those records.
- Records are created only when a value is written. Below an element with
  `__NEW_DATASET__`, elements no longer split records, and each occurrence of
  any element carrying it starts a new record.
- External values are scoped to the element that encloses their source and
  their use, and may be used before they appear in the document.
- Profiles are validated strictly, with a line and column for each problem:
  unknown modifiers or directives, fields without a dataset, inconsistent
  indentation, directives naming something the profile never produces, and
  names that are both ignored and captured. Repeated names merge.
- `parse_using_profile()` takes its options as keyword arguments. With
  `dispatch`, it returns the datasets that have no dispatcher (`{}` when all
  are dispatched); per-dataset dispatch settings fall back to `__generic__`.
- Process functions are checked before parsing.
- `python -m xmldataset` runs the command-line tool.
- Python 3.11 or newer is required.
- Packaging moved to `pyproject.toml`; CI moved to GitHub Actions; releases are
  published with PyPI Trusted Publishing.
- Documentation rewritten, with every example shown as text, YAML and JSON and
  tested on each build.

### Removed

- The private `_XMLDataset` class, and the built-in `python -m xmldataset` demo.
- Python 2 and Python 3.10 and older.

### Fixed

- Records when an element is missing some of its fields.
- `global_values` on records started by `__NEW_DATASET__` or external values.
- An unindented field line, such as `catalog = dataset:d`.
- Indentation that does not line up with an outer level.
- `dispatch` configured for only some datasets.
- The error for a missing `__DATASET_PROCESSING__` function.
- A `SyntaxWarning` on import with Python 3.12 and newer.
- The level of the `"default"` logger is no longer changed.

## 1.0.4 - 2020-05-30

### Changed

- History update.

## 1.0.3 - 2020-05-30

### Changed

- Documentation, awesome badge.

## 1.0.2 - 2020-05-30

### Added

- Python 3.7 and 3.8 to the test matrix.

### Removed

- Python 2.6 and 3.3 from the test matrix (no longer supported).

### Fixed

- Duplicate results (thanks @davidmarcano).

### Changed

- Code formatted with black.

## 1.0.1 - 2016-10-14

### Changed

- Tidied up core for main execution example (use `python -m xmldataset` to run the
  inbuilt example).
- Added use of pandas to the quickstart.
- Added Python 3.4 to the test matrix.

## 1.0.0 - 2016-06-18

### Changed

- First official release, revamped documentation.

## 0.1.7 - 2015-06-02

### Added

- `global_values` option for `parse_using_profile`. When supplied as a dictionary, all
  entries in the dictionary are merged into new datasets, for example
  `parse_using_profile(xml, profile, global_values={"location": "Chorleywood"})`.

## 0.1.6 - 2014-09-24

### Changed

- The `default` option works with nested defaults. If a level in the XML structure is not
  traversed but contains defaults, `__ALWAYS_FOLLOW__ = entry` tells the parser to follow
  the profile entry and set the defaults.

## 0.1.5 - 2014-09-08

### Added

- `__DATASET_PROCESSING__ = dataset:process`, which processes a dataset against a
  function supplied through the `process` option.

## 0.1.4 - 2014-08-27

### Added

- `default` option in the profile markup, which sets a value when the context is missing
  from the XML: `default:` results in `''` and `default:Missing` results in `'Missing'`.

## 0.1.3 - 2014-08-17

### Changed

- Minor updates to supporting documents.

## 0.1.2 - 2014-08-17

### Changed

- Minor updates to supporting documents.

## 0.1.1 - 2014-08-17

### Changed

- Minor updates to supporting documents.

## 0.1.0 - 2014-08-17

### Added

- First release on PyPI.
