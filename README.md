# jailbreak-corpus-mini-py

[![PyPI](https://img.shields.io/pypi/v/jailbreak-corpus-mini-py.svg)](https://pypi.org/project/jailbreak-corpus-mini-py/)
[![Python](https://img.shields.io/pypi/pyversions/jailbreak-corpus-mini-py.svg)](https://pypi.org/project/jailbreak-corpus-mini-py/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Small local jailbreak and prompt-injection fixture set for tests.** Ships a JSON corpus of canonical attack prompts (instruction override, prompt leak, excessive agency, encoding tricks, role hijack) with category + severity labels you can pivot on. Zero runtime dependencies.

Python port of [@mukundakatta/jailbreak-corpus-mini](https://github.com/MukundaKatta/jailbreak-corpus-mini).

## Install

```bash
pip install jailbreak-corpus-mini-py
```

## Usage

```python
from jailbreak_corpus_mini import (
    load_corpus,
    get_jailbreak_fixtures,
    fixture_texts,
    Fixture,
)

# Full corpus (each entry is a Fixture: {id, prompt, category, severity, text}).
corpus = load_corpus()
len(corpus)                    # > 5
corpus[0].prompt               # canonical attack string
corpus[0].category             # e.g. "prompt_injection"
corpus[0].severity             # "low" | "medium" | "high"

# Filter to a single category (matches JS sibling's getJailbreakFixtures).
get_jailbreak_fixtures(category="prompt_injection")

# Just the raw strings (handy for hooking into a guardrail eval loop).
texts = fixture_texts(severity="high")
```

## Use it in a guardrail test

```python
import pytest
from jailbreak_corpus_mini import load_corpus

def my_guardrail(prompt: str) -> bool:
    """Return True if prompt should be blocked."""
    ...

@pytest.mark.parametrize("fixture", load_corpus())
def test_guardrail_blocks_known_attacks(fixture):
    assert my_guardrail(fixture.prompt), (
        f"missed {fixture.category}/{fixture.severity}: {fixture.prompt!r}"
    )
```

## API

| Symbol | Behavior |
|---|---|
| `Fixture` | Dataclass: `id`, `prompt`, `category`, `severity`, plus `text` alias for JS-parity. |
| `load_corpus()` | Returns the full list of `Fixture` objects. |
| `get_jailbreak_fixtures(*, category=None, severity=None, risk=None)` | Filtered view. `risk=` is the JS sibling's name for `category=`. |
| `fixture_texts(...)` | Same filters, returns `list[str]` of prompts only. |

The fixture corpus ships as `corpus.json` inside the package and is loaded once on import. Patch the file (or call `load_corpus_from(path)`) to use your own.

See the JS sibling's [README](https://github.com/MukundaKatta/jailbreak-corpus-mini) for the full design notes.
