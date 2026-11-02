"""Profile formats: the text syntax, YAML/JSON mappings, and the JSON Schema."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from xmldataset import (
    DatasetProcess,
    ExternalReset,
    ExternalValue,
    Field,
    Node,
    Profile,
    ProfileError,
    compile_profile,
    json_schema,
)

CASES = sorted((Path(__file__).parent / "cases").glob("*/*/profile.dsl"))
EXAMPLES = sorted((Path(__file__).parent.parent / "examples").glob("*/profile.dsl"))


# --- text syntax ---------------------------------------------------------------


def test_every_feature_parses_to_the_model() -> None:
    profile = Profile.from_dsl(
        """
# comments and blank lines are ignored

catalog
    shop
        number = external_dataset:shop,name:shop_number
        book
            __NEW_DATASET__ = books
            __NEW_EXTERNAL_VALUE_HOLDER__ = shop:extra
            __ALWAYS_FOLLOW__ = meta
            id     = dataset:books,prefix:book_ dataset:ids
            title  = dataset:books,process:clean,default:"(none)",list:true
            genre  = __IGNORE__
            meta
                isbn = dataset:books,default:
            __EXTERNAL_VALUE__ = shop:shop_number:books shop:shop_number:ids:number
            __DATASET_PROCESSING__ = finish:books
"""
    )
    book = Node(
        "book",
        children=(
            Node(
                "id",
                fields=(Field(dataset="books", prefix="book_"), Field(dataset="ids")),
            ),
            Node(
                "title",
                fields=(
                    Field(
                        dataset="books", process="clean", default="(none)", as_list=True
                    ),
                ),
            ),
            Node("genre", ignore=True),
            Node(
                "meta",
                children=(Node("isbn", fields=(Field(dataset="books", default=""),)),),
            ),
        ),
        new_dataset=("books",),
        external_values=(
            ExternalValue("shop", "shop_number", "books"),
            ExternalValue("shop", "shop_number", "ids", "number"),
        ),
        reset_external_values=(ExternalReset("shop", "extra"),),
        dataset_processing=(DatasetProcess("finish", "books"),),
        always_follow=("meta",),
    )
    number = Node(
        "number", fields=(Field(external_dataset="shop", name="shop_number"),)
    )
    assert profile == Profile(
        (Node("catalog", children=(Node("shop", children=(number, book)),)),)
    )
    assert profile.datasets == ("books", "ids")


def test_duplicate_names_merge_instead_of_overwriting() -> None:
    profile = Profile.from_dsl("r\n  a = external_dataset:x\n  a\n    id = dataset:d")
    assert profile.roots[0].children == (
        Node(
            "a",
            fields=(Field(external_dataset="x"),),
            children=(Node("id", fields=(Field(dataset="d"),)),),
        ),
    )


def test_tabs_are_accepted_when_used_consistently() -> None:
    assert Profile.from_dsl("r\n\ti\n\t\ta = dataset:d") == Profile.from_dsl(
        "r\n i\n  a = dataset:d"
    )


def test_uniformly_indented_profiles_are_accepted() -> None:
    assert Profile.from_dsl(
        "\n        r\n            a = dataset:d\n"
    ) == Profile.from_dsl("r\n  a = dataset:d")


@pytest.mark.parametrize(
    ("text", "message", "line", "column"),
    [
        ("", "the profile is empty", None, None),
        ("r\n\n    a = dataset:d\n  b = dataset:d", "unindent does not match", 4, 3),
        (
            "r\n    i\n        a = dataset:d\n      b = dataset:d",
            "unindent does not match",
            4,
            7,
        ),
        ("r\n  __NEW_DATASET__ = d\n    x", "unexpected indentation", 3, 5),
        ("r\n  a = __IGNORE__\n    x", "unexpected indentation", 3, 5),
        ("  r\n a", "indented less than the first line", 2, 1),
        ("r\n \ta = dataset:d", "mixes tabs and spaces", 2, 1),
        ("r\n\ti\n        a = dataset:d", "tabs and spaces inconsistently", 3, 1),
        ("r\n  a = datset:d", "unknown key 'datset' (did you mean 'dataset'?)", 2, 7),
        ("r\n  a = dataset", "expected key:value", 2, 7),
        ("r\n  a =", "expected at least one field", 2, 6),
        ("r\n  a = name:x", "a field needs dataset: or external_dataset:", 2, 7),
        ("r\n  a = dataset:d,list:yes", "list: must be true or false", 2, 7),
        ('r\n  a = dataset:d,default:"open', "unterminated quoted value", 2, 25),
        ("r\n  a = dataset:d,name:x,name:y", "'name' is given twice", 2, 29),
        ("r\n  a b", "expected '=' or the end of the line", 2, 5),
        (
            "r\n  __NEW_DATASETS__ = d",
            "unknown directive '__NEW_DATASETS__' (did you mean",
            2,
            3,
        ),
        ("__NEW_DATASET__ = d", "must be inside an element", 1, 1),
        ("r\n  __NEW_DATASET__", "needs '=' and a value", 2, 18),
        (
            "r\n  __EXTERNAL_VALUE__ = a:b",
            "expected external_dataset:field:dataset[:name]",
            2,
            24,
        ),
        (
            "r\n  __NEW_EXTERNAL_VALUE_HOLDER__ = a",
            "expected external_dataset:field",
            2,
            35,
        ),
        ("r\n  __DATASET_PROCESSING__ = p:d:x", "expected process:dataset", 2, 28),
        ("r\n  __ALWAYS_FOLLOW__ = missing", "not an element inside 'r'", 2, 23),
        ("r\n  = dataset:d", "expected an element name", 2, 3),
    ],
)
def test_text_syntax_errors_are_located(
    text: str, message: str, line: int | None, column: int | None
) -> None:
    with pytest.raises(ProfileError, match=re.escape(message)) as info:
        Profile.from_dsl(text)
    if line is not None:
        assert (info.value.line, info.value.column) == (line, column)
        assert str(info.value).startswith(f"line {line}, column {column}: ")


def test_text_profile_must_be_a_string() -> None:
    with pytest.raises(TypeError):
        Profile.from_dsl(b"r")  # type: ignore[arg-type]


def test_writer_quotes_values_that_need_it() -> None:
    field = Field(dataset="d", default="Not, Found", name='say "hi"', prefix="")
    text = Profile((Node("r", children=(Node("a", fields=(field,)),)),)).to_dsl()
    assert (
        text
        == 'r\n    a = dataset:d,name:"say \\"hi\\"",prefix:"",default:"Not, Found"\n'
    )
    assert Profile.from_dsl(text).roots[0].children[0].fields == (field,)


@pytest.mark.parametrize(
    "profile",
    [
        Profile((Node("r", new_dataset=("a b",)),)),
        Profile((Node("r", external_values=(ExternalValue("a:b", "c", "d"),)),)),
        Profile((Node("bad name"),)),
    ],
)
def test_writer_rejects_what_the_text_syntax_cannot_express(profile: Profile) -> None:
    with pytest.raises(ProfileError):
        profile.to_dsl()


@pytest.mark.parametrize(
    "path", CASES + EXAMPLES, ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}"
)
def test_text_round_trip(path: Path) -> None:
    profile = Profile.from_dsl(path.read_text(encoding="utf-8"))
    assert Profile.from_dsl(profile.to_dsl()) == profile


# --- structured -------------------------------------------------------------------


def test_structured_shorthands() -> None:
    profile = Profile.from_dict(
        {
            "$schema": "https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json",
            "catalog": {
                "book": {
                    "$new_dataset": "books",
                    "id": 1,
                    "title": ["books", {"dataset": "titles", "name": "book_title"}],
                    "author": {"$dataset": "books", "$process": "upper"},
                    "genre": {"$ignore": True},
                    "empty": None,
                }
            },
        }
    )
    book = profile.roots[0].children[0]
    assert book.new_dataset == ("books",)
    assert [c.fields for c in book.children] == [
        (Field(dataset="1"),),
        (Field(dataset="books"), Field(dataset="titles", name="book_title")),
        (Field(dataset="books", process="upper"),),
        (),
        (),
    ]
    assert book.children[3].ignore


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ([], "a profile must be a mapping"),
        ({}, "the profile is empty"),
        ({"$version": 1}, "unknown top-level setting"),
        (
            {"r": {"$datset": "d"}},
            "unknown setting '\\$datset' \\(did you mean '\\$dataset'\\?\\)",
        ),
        (
            {"r": {"a": {"$name": "x"}}},
            "a field needs \\$dataset or \\$external_dataset",
        ),
        ({"r": {"a": [{"datset": "d"}]}}, "unknown key 'datset'"),
        ({"r": {"a": True}}, "dataset must be a string, not bool"),
        ({"r": {"a": 1.5}}, "not float \\(quote it\\)"),
        ({"r": {"a": "two words"}}, "no spaces"),
        ({"r": {"a": []}}, "expected at least one field"),
        ({"r": {"bad name": "d"}}, "not a valid element"),
        ({"r": {"$ignore": "yes"}}, "\\$ignore must be true or false"),
        (
            {"r": {"a": {"$dataset": "d", "$list": "yes"}}},
            "\\$list must be true or false",
        ),
        ({"r": {"$fields": []}}, "\\$fields must be a non-empty list"),
        ({"r": {"$always_follow": "x"}}, "not an element inside 'r'"),
        (
            {"r": {"$external_values": [{"external_dataset": "x"}]}},
            "missing field, dataset",
        ),
        ({"r": {"$external_values": ["x:y:z"]}}, "expected a mapping"),
        (
            {"r": {"$dataset_processing": [{"process": "p", "dataset": "d", "x": 1}]}},
            "unknown key 'x'",
        ),
        ({"r": {1: "d"}}, "keys must be strings"),
    ],
)
def test_structured_errors_are_located(data: Any, message: str) -> None:
    with pytest.raises(ProfileError, match=message):
        Profile.from_dict(data)


def test_structured_error_location() -> None:
    with pytest.raises(ProfileError) as info:
        Profile.from_dict(
            {"catalog": {"book": {"title": [{"dataset": "d"}, {"name": "x"}]}}}
        )
    assert info.value.location == "catalog > book > title[1]"
    assert str(info.value).startswith("catalog > book > title[1]: ")


def test_yaml_errors_are_reported_with_a_line() -> None:
    with pytest.raises(ProfileError, match="invalid YAML") as info:
        Profile.from_yaml("catalog:\n  book: [unclosed\n")
    assert info.value.line is not None


# --- JSON Schema -----------------------------------------------------------------------


@pytest.fixture(scope="module")
def validator() -> jsonschema.Draft202012Validator:
    schema = json_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


@pytest.mark.parametrize(
    "path", CASES + EXAMPLES, ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}"
)
def test_schema_accepts_every_profile(
    path: Path, validator: jsonschema.Draft202012Validator
) -> None:
    validator.validate(compile_profile(path.read_text(encoding="utf-8")).to_dict())


@pytest.mark.parametrize(
    "data",
    [
        {"r": {"$datset": "d"}},
        {"r": {"a": {"$name": "x"}}},
        {"r": {"a": [{"name": "x"}]}},
        {"r": {"a": True}},
        {"r": {"a": "two words"}},
        {"r": {"$ignore": "yes"}},
        {"r": {"$external_values": [{"external_dataset": "x"}]}},
        {"$version": 1},
        {},
    ],
)
def test_schema_rejects_invalid_profiles(
    data: dict[str, Any], validator: jsonschema.Draft202012Validator
) -> None:
    assert not validator.is_valid(data)
    with pytest.raises(ProfileError):
        Profile.from_dict(data)


def test_schema_file_is_valid_json_with_a_stable_id() -> None:
    schema = json_schema()
    assert (
        schema["$id"]
        == "https://xmldataset.readthedocs.io/en/stable/schema/profile-v1.json"
    )
    assert json.loads(json.dumps(schema)) == schema


# --- regressions from the 2.0 review ----------------------------------------


def test_backslash_only_escapes_quotes_and_backslashes() -> None:
    field = (
        Profile.from_dsl('r\n  a = dataset:d,default:"C:\\Program Files\\\\x \\"q\\""')
        .roots[0]
        .children[0]
        .fields[0]
    )
    assert field.default == 'C:\\Program Files\\x "q"'


@pytest.mark.parametrize(
    "text",
    [
        "r\n  a = dataset:d\n  a = __IGNORE__",
        "r\n  a = __IGNORE__\n  a\n    b = dataset:d",
    ],
)
def test_ignored_names_cannot_also_be_captured(text: str) -> None:
    with pytest.raises(ProfileError, match="'a' is ignored"):
        Profile.from_dsl(text)


def test_ignored_names_cannot_also_be_captured_in_mappings() -> None:
    with pytest.raises(ProfileError, match="'a' is ignored"):
        Profile.from_dict({"r": {"a": {"$ignore": True, "b": "d"}}})


@pytest.mark.parametrize(
    "text",
    [
        "a:\n  title: [{dataset: d, yes: x}]\n",
        "a:\n  title: [{dataset: d, 1: x}]\n",
        "a:\n  title: {$dataset: d, 5: x}\n",
    ],
)
def test_non_string_keys_in_fields_are_profile_errors(text: str) -> None:
    with pytest.raises(ProfileError, match="keys must be strings"):
        Profile.from_yaml(text)


def test_bad_json_is_a_profile_error() -> None:
    with pytest.raises(ProfileError, match="invalid JSON") as info:
        Profile.from_json('{"r": ')
    assert info.value.line == 1
