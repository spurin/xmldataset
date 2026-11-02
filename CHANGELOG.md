# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Work towards 2.0. Parsing behaviour is unchanged so far.

### Changed

- Python 3.11 or newer is required. Python 2 and Python 3.10 and older are no longer
  supported.
- Packaging moved from `setup.py` to `pyproject.toml` (uv build backend, `src/` layout,
  PEP 639 license metadata).
- `xmldataset.__version__` is now read from the installed package metadata.
- Continuous integration moved from Travis CI to GitHub Actions. Releases are published
  with PyPI Trusted Publishing.
- Documentation uses the Furo theme and supports Markdown pages; the vendored alabaster
  theme was removed.

### Fixed

- Importing xmldataset no longer emits `SyntaxWarning: "\s" is an invalid escape
  sequence` on Python 3.12 and newer.
- The test suite runs on Python 3.12 and newer (`assertRaisesRegexp` was removed from
  `unittest`).

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
