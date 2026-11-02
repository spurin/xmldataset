"""The xmldataset command-line tool."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from xmldataset import compile_profile, json_schema
from xmldataset._cli import main

XML = "<shop><book id='1'><title>Dune</title><tag>a</tag><tag>b</tag></book><book id='2'><title>Emma</title></book></shop>"
PROFILE = "shop\n  book\n    id = dataset:books\n    title = dataset:books dataset:titles\n    tag = dataset:books,list:true\n"


@pytest.fixture
def files(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "doc.xml").write_text(XML)
    (tmp_path / "profile.txt").write_text(PROFILE)
    return tmp_path / "profile.txt", tmp_path / "doc.xml"


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


def test_run_json(files: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "run", str(files[0]), str(files[1]))
    assert code == 0
    assert json.loads(out) == {
        "books": [
            {"id": "1", "title": "Dune", "tag": ["a", "b"]},
            {"id": "2", "title": "Emma"},
        ],
        "titles": [{"title": "Dune"}, {"title": "Emma"}],
    }


def test_run_jsonl_filtered(
    files: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, _ = run(
        capsys, "run", str(files[0]), str(files[1]), "-f", "jsonl", "-d", "titles"
    )
    assert code == 0
    assert [json.loads(line) for line in out.splitlines()] == [
        {"dataset": "titles", "record": {"title": "Dune"}},
        {"dataset": "titles", "record": {"title": "Emma"}},
    ]


def test_run_csv(
    files: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "out.csv"
    code, _, _ = run(
        capsys,
        "run",
        str(files[0]),
        str(files[1]),
        "-f",
        "csv",
        "-d",
        "books",
        "-o",
        str(target),
    )
    assert code == 0
    rows = list(csv.DictReader(io.StringIO(target.read_text())))
    assert rows == [
        {"id": "1", "title": "Dune", "tag": '["a", "b"]'},
        {"id": "2", "title": "Emma", "tag": ""},
    ]


def test_csv_needs_a_dataset_when_there_are_several(files: tuple[Path, Path]) -> None:
    with pytest.raises(SystemExit, match="needs --dataset"):
        main(["run", str(files[0]), str(files[1]), "-f", "csv"])


def test_run_with_globals_namespaces_and_stdin(tmp_path: Path) -> None:
    (tmp_path / "p.yaml").write_text("a:feed:\n  a:entry:\n    title: e\n")
    xml = b'<feed xmlns="urn:a"><entry><title>T</title></entry></feed>'
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xmldataset",
            "run",
            str(tmp_path / "p.yaml"),
            "-",
            "-n",
            "a=urn:a",
            "-g",
            "src=cli",
        ],
        input=xml,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout) == {"e": [{"src": "cli", "title": "T"}]}


def test_convert_between_formats(
    files: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    original = compile_profile(PROFILE)
    for fmt, suffix in [("yaml", ".yaml"), ("json", ".json"), ("dsl", ".txt")]:
        target = tmp_path / f"converted{suffix}"
        assert (
            run(capsys, "convert", str(files[0]), "--to", fmt, "-o", str(target))[0]
            == 0
        )
        assert (
            run(capsys, "validate", str(target))[1] == f"{target}: ok (books, titles)\n"
        )
    code, out, _ = run(capsys, "convert", str(files[0]))
    assert code == 0
    assert compile_profile(__import__("yaml").safe_load(out)) == original


def test_validate_reports_errors_with_locations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.txt"
    bad.write_text("shop\n  book = datset:x\n")
    code, _, err = run(capsys, "validate", str(bad))
    assert code == 1
    assert (
        err
        == f"{bad}: line 2, column 10: unknown key 'datset' (did you mean 'dataset'?)\n"
    )


def test_errors_are_reported_without_a_traceback(
    files: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "broken.xml").write_text("<shop>")
    code, _, err = run(capsys, "run", str(files[0]), str(tmp_path / "broken.xml"))
    assert code == 1
    assert err.startswith("xmldataset: error: no element found")
    code, _, err = run(capsys, "run", str(tmp_path / "missing.txt"), str(files[1]))
    assert code == 1
    assert "No such file" in err


def test_process_functions_cannot_come_from_the_command_line(
    files: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "p.txt").write_text("shop\n  book\n    title = dataset:t,process:up\n")
    code, _, err = run(capsys, "run", str(tmp_path / "p.txt"), str(files[1]))
    assert code == 1
    assert "only be supplied from Python" in err


def test_bad_key_value_option(files: tuple[Path, Path]) -> None:
    with pytest.raises(SystemExit, match="expects KEY=VALUE"):
        main(["run", str(files[0]), str(files[1]), "-g", "novalue"])


def test_schema_and_version(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "schema")
    assert code == 0
    assert json.loads(out) == json_schema()
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert capsys.readouterr().out.startswith("xmldataset 2.")
