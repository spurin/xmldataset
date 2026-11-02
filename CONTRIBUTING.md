# Contributing

Contributions are welcome and greatly appreciated. Every little bit helps, and credit will
always be given.

## Ways to contribute

- **Report bugs** at <https://github.com/spurin/xmldataset/issues>. Please include your
  operating system, Python version, xmldataset version, and the smallest XML and profile
  that reproduce the problem, along with the output you expected.
- **Fix bugs or implement features**: look through the GitHub issues. Anything tagged
  "bug" or "enhancement" is open to whoever wants to work on it.
- **Write documentation**, whether in the official docs, in docstrings, or in blog posts
  and articles.
- **Submit feedback** by filing an issue. If you are proposing a feature, explain in
  detail how it would work and keep the scope as narrow as possible.

## Development setup

The project uses [uv](https://docs.astral.sh/uv/) to manage Python versions, the virtual
environment, and development tools.

1. Fork the repository on GitHub and clone your fork:

   ```console
   git clone git@github.com:your_name_here/xmldataset.git
   cd xmldataset
   ```

2. Create the development environment. This installs xmldataset in editable mode along
   with the test and lint tools:

   ```console
   uv sync
   ```

3. Install the git hooks (optional, but they catch most CI failures before you push).
   [prek](https://github.com/j178/prek) reads the standard `.pre-commit-config.yaml`;
   `pre-commit` works too:

   ```console
   uvx prek install
   ```

4. Create a branch for your change:

   ```console
   git checkout -b name-of-your-bugfix-or-feature
   ```

## Checks

Run these before opening a pull request. CI runs the same commands.

```console
uv run pytest                       # tests
uv run ruff check                   # lint
uv run ruff format                  # format
uv run mypy                         # type check
uv run coverage run -m pytest && uv run coverage report
```

To run the tests on a specific Python version (uv downloads it if needed):

```console
uv run --python 3.11 pytest
```

To build the documentation locally:

```console
uv run --group docs sphinx-build -W -b html docs docs/_build/html
```

## Project layout

| Path | Contents |
| --- | --- |
| `src/xmldataset/_model.py` | The typed profile model every format compiles to |
| `src/xmldataset/_dsl.py` | The text syntax: parser and writer |
| `src/xmldataset/_structured.py` | YAML/JSON/dict profiles; `profile-v1.schema.json` is their JSON Schema |
| `src/xmldataset/_engine.py` | The streaming engine and its record rules |
| `src/xmldataset/_api.py`, `_cli.py` | Public functions and the `xmldataset` command |
| `tests/cases/` | Data-driven test cases (see below) |
| `examples/` | Documentation examples; also run as test cases |
| `tests/legacy/` | The frozen 1.0.4 engine, used only as a test oracle |
| `docs/` | Sphinx + MyST documentation; `docs/_ext/` renders `examples/` |

## Test cases and examples

Each directory in `tests/cases/<group>/` and `examples/` is one case:

- `profile.dsl`: the profile in the text syntax;
- `input.xml`, or an `input = "..."` path in `case.toml`;
- `expected.json`: the output xmldataset must produce;
- `case.toml`: a `description`, optional `[options]`, and `v2_only = true` when
  1.x cannot read the profile;
- `legacy.json`: only when the output deliberately differs from 1.x.

Every case runs three times: with the text profile, and with it converted to
YAML and to JSON. It also runs through the frozen 1.0.4 engine, which must
produce `legacy.json` (or `expected.json` when there is no `legacy.json`). A
behaviour change is therefore always a reviewed file, never an accident.

Adding a directory is enough to add a test. Examples in `examples/` also appear
in the documentation as synchronised Text | YAML | JSON tabs, and the docs build
fails if any of the three formats stops producing `expected.json`.

`pycon` code blocks in `README.md` and `docs/*.md` run as doctests.

## Pull request guidelines

1. Include tests. Bug fixes should come with a test that fails without the fix.
2. If the pull request changes behaviour or adds functionality, update the documentation
   and add an entry under "Unreleased" in `CHANGELOG.md`.
3. The pull request must pass CI on every supported Python version (3.11 and newer).
