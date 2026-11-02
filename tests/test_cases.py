"""Data-driven cases in tests/cases/<group>/<name>/.

Each case directory holds:

- ``profile.dsl``: the profile in the text syntax
- ``input.xml``: the XML, unless ``case.toml`` names a shared ``input`` file
- ``expected.json``: the output xmldataset 2 must produce
- ``legacy.json``: what 1.x produced, only when 2.0 deliberately differs
- ``case.toml``: a description, optional ``input`` and ``[options]``, and
  ``v2_only = true`` for profiles 1.x cannot read

Every case also runs with the profile converted to YAML and to JSON, and through
the frozen 1.0.4 engine to pin the behaviour change (or lack of one).
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

import xmldataset
from tests.legacy.engine import parse_using_profile as legacy_parse

CASES_DIR = Path(__file__).parent / "cases"


@dataclass
class Case:
    path: Path
    xml: str
    profile: str
    expected: Any
    legacy: Any
    options: dict[str, Any]
    v2_only: bool


def load_case(path: Path) -> Case:
    meta = (
        tomllib.loads((path / "case.toml").read_text())
        if (path / "case.toml").exists()
        else {}
    )
    expected = json.loads((path / "expected.json").read_text())
    legacy_file = path / "legacy.json"
    return Case(
        path=path,
        xml=(path / meta.get("input", "input.xml")).read_text(),
        profile=(path / "profile.dsl").read_text(),
        expected=expected,
        legacy=json.loads(legacy_file.read_text())
        if legacy_file.exists()
        else expected,
        options=meta.get("options", {}),
        v2_only=meta.get("v2_only", False),
    )


CASES = sorted(p.parent for p in CASES_DIR.glob("*/*/profile.dsl"))
IDS = [f"{p.parent.name}/{p.name}" for p in CASES]


@pytest.mark.parametrize("path", CASES, ids=IDS)
def test_output_matches_expected(path: Path) -> None:
    case = load_case(path)
    assert (
        xmldataset.parse_using_profile(case.xml, case.profile, **case.options)
        == case.expected
    )


@pytest.mark.parametrize("fmt", ["yaml", "json"])
@pytest.mark.parametrize("path", CASES, ids=IDS)
def test_yaml_and_json_profiles_give_the_same_output(path: Path, fmt: str) -> None:
    case = load_case(path)
    profile = xmldataset.compile_profile(case.profile)
    converted = (
        xmldataset.Profile.from_yaml(profile.to_yaml())
        if fmt == "yaml"
        else xmldataset.Profile.from_json(profile.to_json())
    )
    assert converted == profile
    assert (
        xmldataset.parse_using_profile(case.xml, converted, **case.options)
        == case.expected
    )


@pytest.mark.parametrize("path", CASES, ids=IDS)
def test_legacy_output_is_pinned(path: Path) -> None:
    case = load_case(path)
    if case.v2_only:
        pytest.skip("profile uses 2.0-only syntax")
    assert legacy_parse(case.xml, case.profile, **case.options) == case.legacy
