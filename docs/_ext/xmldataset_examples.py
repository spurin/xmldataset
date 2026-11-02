"""Render examples/<name>/ into Markdown snippets for the docs, after running them.

For every example this writes, under docs/_generated/examples/<name>/:

- ``profile.md``: the profile as synchronised Text | YAML | JSON tabs. YAML and
  JSON are generated from profile.dsl with xmldataset's own converter.
- ``input.md``: the XML input.
- ``output.md``: the output (expected.json).
- ``legacy.md``: what xmldataset 1.x produced, when it differs.

Before writing anything, each example is run with all three profile formats and
must produce expected.json exactly; otherwise the build fails. It also copies
the JSON Schema to a stable URL (schema/profile-v1.json).
"""

from __future__ import annotations

import json
import pydoc
import tomllib
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

import xmldataset

DOCS = Path(__file__).resolve().parent.parent
EXAMPLES = DOCS.parent / "examples"
GENERATED = DOCS / "_generated"


def _fence(language: str, text: str) -> str:
    return f"```{language}\n{text.rstrip()}\n```\n"


def _tab(label: str, sync: str, body: str) -> str:
    return f":::{{tab-item}} {label}\n:sync: {sync}\n\n{body}:::\n"


def _options(meta: dict[str, Any]) -> dict[str, Any]:
    options = dict(meta.get("options", {}))
    if "process" in options:
        options["process"] = {k: pydoc.locate(v) for k, v in options["process"].items()}
    return options


def _render(example: Path, out: Path) -> None:
    meta = tomllib.loads((example / "case.toml").read_text(encoding="utf-8"))
    xml = (example / meta.get("input", "input.xml")).read_text(encoding="utf-8")
    text = (example / "profile.dsl").read_text(encoding="utf-8")
    expected = json.loads((example / "expected.json").read_text(encoding="utf-8"))
    profile = xmldataset.compile_profile(text)
    yaml_text, json_text = profile.to_yaml(), profile.to_json()
    options = _options(meta)
    for label, form in [
        ("text", text),
        ("YAML", xmldataset.Profile.from_yaml(yaml_text)),
        ("JSON", xmldataset.Profile.from_json(json_text)),
    ]:
        got = xmldataset.parse_using_profile(xml, form, **options)
        if got != expected:
            raise ExtensionError(
                f"example {example.name}: the {label} profile produced {got!r},"
                f" but expected.json says {expected!r}"
            )

    out.mkdir(parents=True, exist_ok=True)
    tabs = [
        _tab("Text", "text", _fence("text", text)),
        _tab("YAML", "yaml", _fence("yaml", yaml_text)),
        _tab("JSON", "json", _fence("json", json_text)),
    ]
    (out / "profile.md").write_text(
        "::::{tab-set}\n:sync-group: profile\n\n" + "\n".join(tabs) + "::::\n",
        encoding="utf-8",
    )
    (out / "input.md").write_text(_fence("xml", xml), encoding="utf-8")
    (out / "output.md").write_text(
        _fence("json", json.dumps(expected, indent=2, ensure_ascii=False))
    )
    legacy = example / "legacy.json"
    if legacy.exists():
        (out / "legacy.md").write_text(
            _fence("json", legacy.read_text(encoding="utf-8"))
        )


def generate(app: Sphinx) -> None:
    for example in sorted(p.parent for p in EXAMPLES.glob("*/profile.dsl")):
        _render(example, GENERATED / "examples" / example.name)
    schema_dir = GENERATED / "extra" / "schema"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "profile-v1.json").write_text(
        json.dumps(xmldataset.json_schema(), indent=2) + "\n"
    )


def setup(app: Sphinx) -> dict[str, Any]:
    app.connect("builder-inited", generate)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
