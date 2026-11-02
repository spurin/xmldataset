"""Every ```pycon block in the docs and README runs as a doctest, and the
README example runs as shown.

Blocks on one page share their variables, in page order. (Profile examples in
the docs are rendered from examples/ and checked by test_cases.py.)
"""

from __future__ import annotations

import doctest
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
BLOCK = re.compile(r"^```pycon\n(.*?)^```", re.MULTILINE | re.DOTALL)
FENCE = re.compile(r"^```(\w+)\n(.*?)^```", re.MULTILINE | re.DOTALL)


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_pycon_examples(page: Path) -> None:
    blocks = BLOCK.findall(page.read_text(encoding="utf-8"))
    if not blocks:
        pytest.skip("no pycon examples")
    parser = doctest.DocTestParser()
    runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    globs: dict[str, object] = {}
    for number, block in enumerate(blocks, start=1):
        test = parser.get_doctest(block, globs, f"{page.name}[{number}]", str(page), 0)
        runner.run(test, clear_globs=False)
        globs.update(test.globs)  # DocTest works on a copy
    assert runner.failures == 0, f"{runner.failures} example(s) failed in {page.name}"


def test_readme_example() -> None:
    """The README example runs as shown, with the profile in each format."""
    import xmldataset

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    example = readme.split("## Example\n", 1)[1].split("\n## ", 1)[0]
    blocks: dict[str, list[str]] = {}
    for lang, body in FENCE.findall(example):
        blocks.setdefault(lang, []).append(body)
    [xml] = blocks["xml"]
    [text] = blocks["text"]
    [yaml] = blocks["yaml"]
    [json_profile, output] = blocks["json"]
    code = blocks["python"][0]

    profile = xmldataset.compile_profile(text)
    assert profile.to_yaml().strip() == yaml.strip()
    assert profile.to_json().strip() == json_profile.strip()

    expected = json.dumps(json.loads(output))  # key order matters
    namespace: dict[str, object] = {"xml": xml, "profile": text}
    exec(code, namespace)
    assert json.dumps(namespace["result"]) == expected
    for form in (
        xmldataset.Profile.from_yaml(yaml),
        xmldataset.Profile.from_json(json_profile),
    ):
        assert json.dumps(xmldataset.parse_using_profile(xml, form)) == expected
