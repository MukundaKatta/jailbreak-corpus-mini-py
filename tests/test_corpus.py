"""Tests for the jailbreak_corpus_mini public surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jailbreak_corpus_mini import (
    Fixture,
    fixture_texts,
    fixtures,
    get_jailbreak_fixtures,
    load_corpus,
    load_corpus_from,
)


def test_load_corpus_returns_list_of_fixtures():
    corpus = load_corpus()
    assert len(corpus) >= 5
    assert all(isinstance(f, Fixture) for f in corpus)


def test_every_fixture_has_required_fields():
    for f in load_corpus():
        assert f.id and isinstance(f.id, str)
        assert f.prompt and isinstance(f.prompt, str)
        assert f.category and isinstance(f.category, str)
        assert f.severity in ("low", "medium", "high")


def test_fixture_ids_are_unique():
    ids = [f.id for f in load_corpus()]
    assert len(ids) == len(set(ids))


def test_includes_canonical_npm_seeds():
    # The original npm package shipped these three; keep them stable.
    ids = {f.id for f in load_corpus()}
    assert "ignore" in ids
    assert "developer" in ids
    assert "tool" in ids


def test_module_level_fixtures_matches_load_corpus():
    assert [f.id for f in fixtures] == [f.id for f in load_corpus()]


def test_filter_by_category():
    leaks = get_jailbreak_fixtures(category="prompt_leak")
    assert len(leaks) >= 1
    assert all(f.category == "prompt_leak" for f in leaks)


def test_filter_by_severity_high_only():
    high = get_jailbreak_fixtures(severity="high")
    assert len(high) >= 1
    assert all(f.severity == "high" for f in high)


def test_filter_by_category_and_severity_ands_them():
    out = get_jailbreak_fixtures(category="prompt_injection", severity="high")
    assert all(
        f.category == "prompt_injection" and f.severity == "high" for f in out
    )


def test_risk_alias_matches_category_filter():
    by_risk = get_jailbreak_fixtures(risk="excessive_agency")
    by_cat = get_jailbreak_fixtures(category="excessive_agency")
    assert [f.id for f in by_risk] == [f.id for f in by_cat]


def test_fixture_texts_returns_just_strings():
    out = fixture_texts(severity="medium")
    assert all(isinstance(s, str) for s in out)


def test_fixture_text_alias_equals_prompt():
    f = load_corpus()[0]
    assert f.text == f.prompt
    assert f.risk == f.category


def test_fixture_is_frozen():
    f = load_corpus()[0]
    with pytest.raises(Exception):
        f.id = "other"  # type: ignore[misc]


def test_load_corpus_from_custom_file(tmp_path: Path):
    custom = tmp_path / "c.json"
    custom.write_text(
        json.dumps(
            [
                {"id": "x", "text": "hi", "risk": "test", "severity": "low"},
            ]
        ),
        encoding="utf-8",
    )
    out = load_corpus_from(custom)
    assert len(out) == 1
    assert out[0].id == "x"
    assert out[0].prompt == "hi"
    assert out[0].category == "test"


def test_load_corpus_from_rejects_non_list(tmp_path: Path):
    bad = tmp_path / "b.json"
    bad.write_text(json.dumps({"id": "x"}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_corpus_from(bad)


def test_load_corpus_from_rejects_missing_fields(tmp_path: Path):
    bad = tmp_path / "b.json"
    bad.write_text(
        json.dumps([{"id": "x", "severity": "low"}]),  # missing prompt + category
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_corpus_from(bad)


def test_load_corpus_from_rejects_bad_severity(tmp_path: Path):
    bad = tmp_path / "b.json"
    bad.write_text(
        json.dumps(
            [
                {
                    "id": "x",
                    "prompt": "p",
                    "category": "c",
                    "severity": "extreme",
                },
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_corpus_from(bad)
