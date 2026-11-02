"""Behaviour of the public API beyond what the data-driven cases cover."""

from __future__ import annotations

import io
import json
import logging
import tracemalloc
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest

import xmldataset
from xmldataset import (
    ConfigurationError,
    MissingProcessError,
    ProfileError,
    iter_records,
    parse_using_profile,
)

CASES = Path(__file__).parent / "cases"
CATALOG = (CASES / "_fixtures" / "catalog.xml").read_text()
BOOKS = (CASES / "v1_suite" / "single_dataset" / "profile.dsl").read_text()
BOOKS_EXPECTED = json.loads(
    (CASES / "v1_suite" / "single_dataset" / "expected.json").read_text()
)
TWO_DATASETS = (CASES / "v1_suite" / "multi_datasets" / "profile.dsl").read_text()
TWO_EXPECTED = json.loads(
    (CASES / "v1_suite" / "multi_datasets" / "expected.json").read_text()
)
SIMPLE = "r\n    i\n        a = dataset:d\n        b = dataset:d"


# --- process -----------------------------------------------------------------


def test_process_transforms_values() -> None:
    profile = BOOKS.replace("author = dataset:1", "author = dataset:1,process:to_upper")
    output = parse_using_profile(CATALOG, profile, process={"to_upper": str.upper})
    expected = [{**r, "author": r["author"].upper()} for r in BOOKS_EXPECTED["1"]]
    assert output == {"1": expected}


def test_process_applies_to_defaults() -> None:
    profile = "r\n  i\n    a = dataset:d,default:x,process:up"
    assert parse_using_profile("<r><i/></r>", profile, process={"up": str.upper}) == {
        "d": [{"a": "X"}]
    }


def test_missing_process_definition_is_reported_before_reading_xml() -> None:
    profile = "r\n  a = dataset:d,process:to_upper"
    with pytest.raises(
        MissingProcessError, match="process definition not supplied as argument"
    ):
        parse_using_profile("<not xml", profile)


def test_missing_process_name_is_reported() -> None:
    profile = "r\n  a = dataset:d,process:to_upper"
    with pytest.raises(MissingProcessError, match="process coderef to_upper missing"):
        parse_using_profile("<r/>", profile, process={"other": str})


def test_dataset_processing_edits_the_current_record() -> None:
    profile = "r\n  i\n    a = dataset:d\n    __DATASET_PROCESSING__ = tag:d"

    def tag(record: dict[str, Any]) -> None:
        record["tagged"] = True

    output = parse_using_profile(
        "<r><i><a>1</a></i><i><a>2</a></i></r>", profile, process={"tag": tag}
    )
    assert output == {"d": [{"a": "1", "tagged": True}, {"a": "2", "tagged": True}]}


def test_dataset_processing_with_missing_process_has_a_clear_error() -> None:
    profile = "r\n  i\n    a = dataset:d\n    __DATASET_PROCESSING__ = nope:d"
    with pytest.raises(MissingProcessError, match="process coderef nope missing"):
        parse_using_profile("<r/>", profile, process={"other": str})


# --- dispatch ----------------------------------------------------------------


def test_generic_dispatch_receives_whole_datasets() -> None:
    received: list[dict[str, list[dict[str, Any]]]] = []
    output = parse_using_profile(
        CATALOG,
        TWO_DATASETS,
        dispatch={"__generic__": {"coderef": received.append, "counter": 100}},
    )
    assert output == {}
    assert received == [{"1": TWO_EXPECTED["1"]}, {"2": TWO_EXPECTED["2"]}]


def test_dispatch_batches_by_counter() -> None:
    one: list[Any] = []
    two: list[Any] = []
    parse_using_profile(
        CATALOG,
        TWO_DATASETS,
        dispatch={
            "1": {"coderef": one.append, "counter": 2},
            "2": {"coderef": two.append, "counter": 5},
        },
    )
    records = TWO_EXPECTED["1"]
    assert one == [{"1": records[i : i + 2]} for i in range(0, len(records), 2)]
    assert [len(batch["2"]) for batch in two] == [5, 5, 2]


@pytest.mark.parametrize("counter", [0, 1])
def test_dispatch_counter_zero_or_one_sends_single_records(counter: int) -> None:
    got: list[Any] = []
    parse_using_profile(
        CATALOG, BOOKS, dispatch={"1": {"coderef": got.append, "counter": counter}}
    )
    assert [batch["1"] for batch in got] == [[r] for r in BOOKS_EXPECTED["1"]]


def test_datasets_without_a_dispatcher_are_returned() -> None:
    got: list[Any] = []
    output = parse_using_profile(
        CATALOG, TWO_DATASETS, dispatch={"1": {"coderef": got.append}}
    )
    assert output == {"2": TWO_EXPECTED["2"]}
    assert sum(len(batch["1"]) for batch in got) == len(TWO_EXPECTED["1"])


def test_per_dataset_settings_fall_back_to_generic() -> None:
    got: list[Any] = []
    parse_using_profile(
        CATALOG,
        BOOKS,
        dispatch={"__generic__": {"coderef": got.append}, "1": {"counter": 4}},
    )
    assert [len(batch["1"]) for batch in got] == [4, 4, 4]


@pytest.mark.parametrize(
    ("dispatch", "message"),
    [
        ("nope", "dispatch must map"),
        ({"d": "nope"}, r"dispatch\['d'\] must be a mapping"),
        ({"d": {"count": 1}}, "unknown keys"),
        ({"d": {"counter": -1}}, "must be an int >= 0"),
        ({"d": {"counter": True}}, "must be an int >= 0"),
        ({"d": {"coderef": 3}}, "must be callable"),
    ],
)
def test_invalid_dispatch_settings(dispatch: Any, message: str) -> None:
    with pytest.raises(ConfigurationError, match=message):
        parse_using_profile("<r/>", SIMPLE, dispatch=dispatch)


# --- options -----------------------------------------------------------------


def test_global_values_are_added_to_every_record() -> None:
    profile = "r\n  i\n    __NEW_DATASET__ = d\n    a = dataset:d"
    output = parse_using_profile(
        "<r><i><a>1</a></i><i><a>2</a></i></r>", profile, global_values={"g": 1}
    )
    assert output == {"d": [{"g": 1, "a": "1"}, {"g": 1, "a": "2"}]}


def test_unknown_options_are_rejected() -> None:
    with pytest.raises(TypeError, match="global_value"):
        parse_using_profile("<r/>", SIMPLE, global_value={"g": 1})  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"process": ["f"]}, "process must map"),
        ({"process": {"f": 1}}, "is not callable"),
        ({"global_values": ["g"]}, "global_values must be a mapping"),
        ({"namespaces": {"a": 1}}, "namespaces must map"),
    ],
)
def test_invalid_options(kwargs: dict[str, Any], message: str) -> None:
    profile = "r\n  a = dataset:d,process:f" if "process" in kwargs else SIMPLE
    with pytest.raises(ConfigurationError, match=message):
        parse_using_profile("<r/>", profile, **kwargs)


def test_parsing_does_not_touch_logging() -> None:
    before = {
        name: logging.getLogger(name).level for name in ("", "default", "xmldataset")
    }
    parse_using_profile(CATALOG, BOOKS)
    after = {name: logging.getLogger(name).level for name in before}
    assert before == after


# --- inputs ------------------------------------------------------------------

SMALL = "<r><i><a>1</a><b>2</b></i></r>"
SMALL_EXPECTED = {"d": [{"a": "1", "b": "2"}]}


def test_bytes_and_bytearray() -> None:
    assert parse_using_profile(SMALL.encode(), SIMPLE) == SMALL_EXPECTED
    assert parse_using_profile(bytearray(SMALL.encode()), SIMPLE) == SMALL_EXPECTED


def test_encoding_declaration_in_bytes_is_honoured() -> None:
    xml = '<?xml version="1.0" encoding="ISO-8859-1"?><r><i><a>caf\xe9</a></i></r>'.encode(
        "latin-1"
    )
    assert parse_using_profile(xml, SIMPLE) == {"d": [{"a": "caf\xe9"}]}


def test_str_with_encoding_declaration() -> None:
    xml = '<?xml version="1.0" encoding="UTF-8"?>' + SMALL
    assert parse_using_profile(xml, SIMPLE) == SMALL_EXPECTED


def test_path_and_file_objects(tmp_path: Path) -> None:
    file = tmp_path / "doc.xml"
    file.write_text(SMALL)
    assert parse_using_profile(file, SIMPLE) == SMALL_EXPECTED
    with file.open("rb") as binary:
        assert parse_using_profile(binary, SIMPLE) == SMALL_EXPECTED
    assert parse_using_profile(io.StringIO(SMALL), SIMPLE) == SMALL_EXPECTED


def test_a_str_that_is_a_file_name_gets_a_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "doc.xml").write_text(SMALL)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigurationError, match=r"pathlib.Path"):
        parse_using_profile("doc.xml", SIMPLE)


def test_parsed_elements_are_accepted_and_left_intact() -> None:
    root = ET.fromstring(SMALL)
    assert parse_using_profile(root, SIMPLE) == SMALL_EXPECTED
    assert parse_using_profile(ET.ElementTree(root), SIMPLE) == SMALL_EXPECTED
    assert ET.tostring(root, encoding="unicode") == SMALL


def test_unsupported_input_type() -> None:
    with pytest.raises(TypeError, match="xml must be"):
        list(iter_records(42, SIMPLE))  # type: ignore[arg-type]


def test_malformed_xml_raises_parse_error() -> None:
    with pytest.raises(ET.ParseError):
        parse_using_profile("<r><i></r>", SIMPLE)


# --- values ------------------------------------------------------------------


def test_empty_element_gives_none_and_mixed_content_gives_leading_text() -> None:
    profile = "r\n  i\n    a = dataset:d\n    b = dataset:d"
    xml = "<r><i><a/><b>Hello <x>World</x>!</b></i></r>"
    assert parse_using_profile(xml, profile) == {"d": [{"a": None, "b": "Hello "}]}


def test_values_with_spaces_colons_and_equals() -> None:
    profile = 'r\n  i\n    a = dataset:d\n    b = dataset:d,default:"Not Found"\n    c = dataset:d,default:12:30\n    e = dataset:d,default:x=y'
    assert parse_using_profile("<r><i><a>1</a></i></r>", profile) == {
        "d": [{"a": "1", "b": "Not Found", "c": "12:30", "e": "x=y"}]
    }


def test_list_fields_collect_repeated_values() -> None:
    profile = "people\n  person\n    name = dataset:p\n    phones\n      phone = dataset:p,list:true"
    xml = (
        "<people><person><name>Ann</name><phones><phone>1</phone><phone>2</phone></phones></person>"
        "<person><name>Bob</name><phones><phone>3</phone></phones></person></people>"
    )
    assert parse_using_profile(xml, profile) == {
        "p": [{"name": "Ann", "phone": ["1", "2"]}, {"name": "Bob", "phone": ["3"]}]
    }


def test_attribute_nested_under_a_field_line() -> None:  # issue 13
    profile = (
        "document\n    amount = dataset:records\n        currency = dataset:records"
    )
    xml = '<document><amount currency="USD">123.00</amount><amount currency="EUR">9</amount></document>'
    assert parse_using_profile(xml, profile) == {
        "records": [
            {"amount": "123.00", "currency": "USD"},
            {"amount": "9", "currency": "EUR"},
        ]
    }


# --- namespaces --------------------------------------------------------------

ATOM = '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:x="urn:x"><entry x:id="7"><title>T</title></entry></feed>'


def test_unprefixed_names_match_any_namespace() -> None:
    profile = "feed\n  entry\n    id = dataset:e\n    title = dataset:e"
    assert parse_using_profile(ATOM, profile) == {"e": [{"id": "7", "title": "T"}]}


def test_prefixed_names_use_the_namespaces_option() -> None:
    profile = "atom:feed\n  atom:entry\n    x:id = dataset:e,name:id\n    atom:title = dataset:e,name:title"
    namespaces = {"atom": "http://www.w3.org/2005/Atom", "x": "urn:x"}
    assert parse_using_profile(ATOM, profile, namespaces=namespaces) == {
        "e": [{"id": "7", "title": "T"}]
    }
    # A prefix bound to a different URI does not match.
    assert parse_using_profile(
        ATOM, profile, namespaces={**namespaces, "x": "urn:other"}
    ) == {"e": [{"title": "T"}]}


def test_clark_notation_matches_exactly() -> None:
    profile = "{http://www.w3.org/2005/Atom}feed\n  {http://www.w3.org/2005/Atom}entry\n    title = dataset:e"
    assert parse_using_profile(ATOM, profile) == {"e": [{"title": "T"}]}


def test_undeclared_prefix_is_an_error() -> None:
    with pytest.raises(ConfigurationError, match="namespace prefix 'atom'"):
        parse_using_profile(ATOM, "atom:feed\n  title = dataset:e")


def test_xml_prefix_is_predefined() -> None:
    profile = "r\n  i\n    xml:lang = dataset:d,name:lang"
    assert parse_using_profile('<r><i xml:lang="en"/></r>', profile) == {
        "d": [{"lang": "en"}]
    }


# --- streaming ---------------------------------------------------------------


def test_records_are_yielded_before_the_document_ends() -> None:
    def chunks() -> Iterator[bytes]:
        yield b"<r>" + b"<i><a>1</a></i>" * 3
        raise AssertionError("read past the records we asked for")

    class Source(io.RawIOBase):
        def __init__(self) -> None:
            self.it = chunks()

        def read(self, size: int = -1) -> bytes:
            return next(self.it)

    records = iter_records(cast(Any, Source()), "r\n  i\n    a = dataset:d")
    assert next(records) == ("d", {"a": "1"})
    assert next(records) == ("d", {"a": "1"})


def test_memory_stays_flat_for_large_documents(tmp_path: Path) -> None:
    file = tmp_path / "big.xml"
    with file.open("w") as fh:
        fh.write("<catalog>")
        for i in range(100_000):
            fh.write(f"<book id='{i}'><title>T{i}</title><author>A{i}</author></book>")
        fh.write("</catalog>")
    profile = "catalog\n  book\n    id = dataset:b\n    title = dataset:b\n    author = dataset:b"
    tracemalloc.start()
    try:
        count = sum(1 for _ in iter_records(file, profile))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert count == 100_000
    assert peak < 5_000_000, (
        f"peak {peak / 1e6:.1f} MB for a {file.stat().st_size / 1e6:.1f} MB file"
    )


def _nested(depth: int) -> str:
    opening = "".join(f"<n{i}>" for i in range(depth))
    return f"<r><v>1</v>{opening}x{''.join(f'</n{i}>' for i in reversed(range(depth)))}<v>2</v></r>"


def test_deep_documents_do_not_hit_the_recursion_limit() -> None:
    assert parse_using_profile(_nested(20_000), "r\n  v = dataset:d") == {
        "d": [{"v": "1"}, {"v": "2"}]
    }


def test_deep_profiles() -> None:
    depth = 200
    lines = [" " * (i + 1) + f"n{i}" for i in range(depth - 1)]
    profile = (
        "r\n" + "\n".join(lines) + "\n" + " " * depth + f"n{depth - 1} = dataset:x"
    )
    assert parse_using_profile(_nested(depth), profile) == {
        "x": [{f"n{depth - 1}": "x"}]
    }


def test_parent_value_after_the_children_reaches_every_child_record() -> None:
    profile = "r\n  shop\n    manager = dataset:d\n    book\n      title = dataset:d"
    xml = (
        "<r><shop><book><title>T1</title></book><book><title>T2</title></book><manager>M1</manager></shop>"
        "<shop><book><title>T3</title></book><manager>M2</manager></shop></r>"
    )
    assert parse_using_profile(xml, profile) == {
        "d": [
            {"title": "T1", "manager": "M1"},
            {"title": "T2", "manager": "M1"},
            {"title": "T3", "manager": "M2"},
        ]
    }


def test_dataset_order_follows_first_record() -> None:
    profile = "r\n  i\n    b = dataset:second\n    a = dataset:first"
    output = parse_using_profile("<r><i><b>1</b><a>2</a></i></r>", profile)
    assert list(output) == ["second", "first"]


# --- compiling ---------------------------------------------------------------


def test_compile_profile_accepts_every_form() -> None:
    profile = xmldataset.compile_profile(SIMPLE)
    assert xmldataset.compile_profile(profile) is profile
    assert xmldataset.compile_profile(profile.to_dict()) == profile
    assert profile.datasets == ("d",)
    with pytest.raises(TypeError, match="profile must be"):
        xmldataset.compile_profile(42)  # type: ignore[arg-type]


def test_load_profile_picks_the_format_from_the_extension(tmp_path: Path) -> None:
    profile = xmldataset.compile_profile(SIMPLE)
    for name, text in [
        ("p.txt", profile.to_dsl()),
        ("p.yaml", profile.to_yaml()),
        ("p.json", profile.to_json()),
    ]:
        (tmp_path / name).write_text(text)
        assert xmldataset.load_profile(tmp_path / name) == profile


def test_load_profile_reports_bad_json(tmp_path: Path) -> None:
    (tmp_path / "p.json").write_text('{"r": ')
    with pytest.raises(ProfileError, match="invalid JSON") as info:
        xmldataset.load_profile(tmp_path / "p.json")
    assert info.value.line == 1


def test_version() -> None:
    assert xmldataset.__version__.startswith("2.")
