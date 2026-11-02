"""Property-based tests: invariants that must hold for any document or profile."""

from __future__ import annotations

import contextlib
import io
import string
import xml.etree.ElementTree as ET
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

import xmldataset._engine
from tests.legacy.engine import parse_using_profile as legacy_parse
from xmldataset import (
    ExternalValue,
    Field,
    Node,
    Profile,
    ProfileError,
    parse_using_profile,
)

FIELDS = ("a", "b", "c")
RECORDS = "root\n  rec\n    a = dataset:d\n    b = dataset:d\n    c = dataset:d"

# Each record element: the fields it contains, in document order.
record_elements = st.lists(st.lists(st.sampled_from(FIELDS), unique=True), max_size=8)


def records_xml(elements: list[list[str]]) -> str:
    body = "".join(
        "<rec>" + "".join(f"<{f}>{i}-{f}</{f}>" for f in fields) + "</rec>"
        for i, fields in enumerate(elements)
    )
    return f"<root>{body}</root>"


@given(record_elements)
def test_every_record_comes_from_exactly_one_element(elements: list[list[str]]) -> None:
    output = parse_using_profile(records_xml(elements), RECORDS)
    expected = [
        {f: f"{i}-{f}" for f in fields} for i, fields in enumerate(elements) if fields
    ]
    assert output == ({"d": expected} if expected else {})


@given(
    st.lists(st.just(list(FIELDS)), max_size=6).flatmap(
        lambda els: st.tuples(st.just(els), st.permutations(FIELDS))
    )
)
def test_matches_1x_when_every_record_is_complete(
    case: tuple[list[list[str]], list[str]],
) -> None:
    elements, order = case
    xml = records_xml([list(order) for _ in elements])
    assert parse_using_profile(xml, RECORDS) == legacy_parse(xml, RECORDS)


# Shops with a number attribute, a manager element (before or after the books, or
# missing), and books with an optional author.
shops = st.lists(
    st.tuples(
        st.sampled_from(["before", "after", "missing"]),
        st.lists(st.booleans(), max_size=4),
    ),
    max_size=4,
)
SHOP_PROFILE = (
    "root\n  shop\n    number = dataset:d\n    manager = dataset:d\n"
    "    book\n      title = dataset:d\n      author = dataset:d"
)


@given(shops)
def test_enclosing_values_reach_every_record_inside(
    spec: list[tuple[str, list[bool]]],
) -> None:
    parts, expected = [], []
    for s, (manager, books) in enumerate(spec):
        inner = "".join(
            f"<book><title>T{s}.{b}</title>"
            + (f"<author>A{s}.{b}</author>" if has_author else "")
            + "</book>"
            for b, has_author in enumerate(books)
        )
        m = f"<manager>M{s}</manager>"
        parts.append(
            f'<shop number="{s}">'
            + (m if manager == "before" else "")
            + inner
            + (m if manager == "after" else "")
            + "</shop>"
        )
        shop_values = {"number": str(s)} | (
            {"manager": f"M{s}"} if manager != "missing" else {}
        )
        if not books:
            expected.append(shop_values)
        for b, has_author in enumerate(books):
            expected.append(
                shop_values
                | {"title": f"T{s}.{b}"}
                | ({"author": f"A{s}.{b}"} if has_author else {})
            )
    output = parse_using_profile("<root>" + "".join(parts) + "</root>", SHOP_PROFILE)
    assert output == ({"d": expected} if expected else {})


@pytest.mark.parametrize("chunk_size", [1, 3, 17])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@given(spec=shops)
def test_output_does_not_depend_on_chunking(
    spec: list[tuple[str, list[bool]]], chunk_size: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    xml = (
        "<root>"
        + "".join(
            f'<shop number="{s}">'
            + "".join(f"<book><title>T{b}</title></book>" for b in range(len(books)))
            + ("<manager>M</manager>" if m != "missing" else "")
            + "</shop>"
            for s, (m, books) in enumerate(spec)
        )
        + "</root>"
    )
    whole = parse_using_profile(xml, SHOP_PROFILE)
    monkeypatch.setattr(xmldataset._engine, "CHUNK_SIZE", chunk_size)
    assert parse_using_profile(xml, SHOP_PROFILE) == whole
    assert parse_using_profile(xml.encode(), SHOP_PROFILE) == whole
    assert parse_using_profile(io.BytesIO(xml.encode()), SHOP_PROFILE) == whole
    assert parse_using_profile(ET.fromstring(xml), SHOP_PROFILE) == whole


# --- profile round trips ----------------------------------------------------------

LINE_BREAKS = "\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029"
simple_names = st.text(string.ascii_lowercase + "_", min_size=1, max_size=5).filter(
    lambda s: not (s.startswith("__") and s.endswith("__"))
)
dataset_names = st.text(
    string.ascii_letters + string.digits + "_-.,'\"", min_size=1, max_size=6
)
any_text = st.text(
    st.characters(exclude_characters=LINE_BREAKS, exclude_categories=["Cs"]),
    max_size=8,
)

fields = st.builds(
    Field,
    dataset=st.one_of(st.none(), dataset_names),
    external_dataset=st.one_of(st.none(), simple_names),
    name=st.one_of(st.none(), any_text.filter(bool)),
    prefix=st.one_of(st.none(), any_text),
    process=st.one_of(st.none(), simple_names),
    default=st.one_of(st.none(), any_text),
    as_list=st.booleans(),
).filter(lambda f: f.dataset is not None or f.external_dataset is not None)


def nodes(depth: int) -> st.SearchStrategy[Node]:
    children = (
        st.just(())
        if depth == 0
        else st.lists(nodes(depth - 1), max_size=3, unique_by=lambda n: n.name).map(
            tuple
        )
    )
    return st.builds(
        Node,
        name=simple_names,
        fields=st.lists(fields, max_size=2).map(tuple),
        children=children,
        ignore=st.booleans(),
        new_dataset=st.lists(simple_names, max_size=2, unique=True).map(tuple),
        external_values=st.lists(
            st.builds(
                ExternalValue,
                simple_names,
                simple_names,
                simple_names,
                st.one_of(st.none(), simple_names),
            ),
            max_size=2,
        ).map(tuple),
    )


profiles = st.lists(nodes(2), min_size=1, max_size=2, unique_by=lambda n: n.name).map(
    lambda roots: Profile(tuple(roots))
)


@given(profiles)
def test_every_format_round_trips(profile: Profile) -> None:
    assert Profile.from_dsl(profile.to_dsl()) == profile
    assert Profile.from_dict(profile.to_dict()) == profile
    assert Profile.from_json(profile.to_json()) == profile
    assert Profile.from_yaml(profile.to_yaml()) == profile


@given(st.text(max_size=200))
def test_the_text_parser_only_raises_profile_errors(text: str) -> None:
    with contextlib.suppress(ProfileError):
        Profile.from_dsl(text)


json_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.text(max_size=5),
    lambda inner: (
        st.lists(inner, max_size=3)
        | st.dictionaries(st.text(max_size=5), inner, max_size=3)
    ),
    max_leaves=12,
)


@given(json_values)
def test_the_mapping_reader_only_raises_profile_errors(data: Any) -> None:
    with contextlib.suppress(ProfileError):
        Profile.from_dict(data)
