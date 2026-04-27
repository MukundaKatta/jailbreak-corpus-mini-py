"""jailbreak_corpus_mini -- small local jailbreak and prompt-injection fixtures.

Public surface (mirrors the JS sibling, plus Pythonic helpers):

    from jailbreak_corpus_mini import (
        Fixture,
        load_corpus,
        load_corpus_from,
        get_jailbreak_fixtures,
        fixture_texts,
    )

The fixture data lives in ``corpus.json`` inside the package; tests can patch
that path or call :func:`load_corpus_from` with a custom file.
"""

from .corpus import (
    Fixture,
    fixture_texts,
    fixtures,
    get_jailbreak_fixtures,
    load_corpus,
    load_corpus_from,
)

# JS-name aliases for cross-language search-and-port parity.
getJailbreakFixtures = get_jailbreak_fixtures
fixtureTexts = fixture_texts

__version__ = "0.1.0"
VERSION = __version__

__all__ = [
    "VERSION",
    "Fixture",
    "fixture_texts",
    "fixtureTexts",
    "fixtures",
    "get_jailbreak_fixtures",
    "getJailbreakFixtures",
    "load_corpus",
    "load_corpus_from",
]
