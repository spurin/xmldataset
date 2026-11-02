"""The examples in docstrings (shown on the API reference page) must run."""

from __future__ import annotations

import doctest
from types import ModuleType

import pytest

import xmldataset
from xmldataset import _api, _dsl, _engine, _errors, _model, _structured

MODULES = [xmldataset, _api, _dsl, _engine, _errors, _model, _structured]


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__)
def test_docstring_examples(module: ModuleType) -> None:
    result = doctest.testmod(module, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert result.failed == 0
