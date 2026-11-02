"""Every ```pycon block in the docs and README runs as a doctest.

Blocks on one page share their variables, in page order. (Profile examples in
the docs are rendered from examples/ and checked by test_cases.py.)
"""

from __future__ import annotations

import doctest
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
BLOCK = re.compile(r"^```pycon\n(.*?)^```", re.MULTILINE | re.DOTALL)


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


def test_readme_yaml_and_json_match_the_converter() -> None:
    import xmldataset

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    profile = xmldataset.compile_profile(
        "colleagues\n    colleague\n        title = dataset:colleagues\n"
        "        email = dataset:colleagues,default:none\n"
    )
    assert profile.to_yaml().strip() in readme
    assert profile.to_json().strip() in readme
