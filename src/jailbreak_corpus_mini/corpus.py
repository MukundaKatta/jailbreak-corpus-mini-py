"""Loader for the bundled jailbreak / prompt-injection fixture corpus.

The data lives in ``corpus.json`` next to this module. Each entry has a stable
``id``, the attack ``prompt`` text, a ``category`` (e.g. ``prompt_injection``,
``role_hijack``, ``encoding_smuggle``) and a ``severity`` of ``low`` /
``medium`` / ``high``.

The JS sibling exposes ``risk`` as the category field; we keep ``risk=`` as
an alias on the filter API so existing port code still works.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

_CORPUS_PATH = Path(__file__).with_name("corpus.json")


@dataclass(frozen=True)
class Fixture:
    """A single jailbreak / prompt-injection fixture.

    Attributes:
        id: Stable identifier (e.g. ``"ignore"``, ``"system_override"``).
        prompt: The attack prompt text.
        category: Coarse-grained label (``prompt_injection``,
            ``prompt_leak``, ``role_hijack``, ``excessive_agency``,
            ``encoding_smuggle``, ``indirect_injection``, ``tool_misuse``,
            ``policy_evasion``).
        severity: ``"low"``, ``"medium"``, or ``"high"``.
    """

    id: str
    prompt: str
    category: str
    severity: str

    @property
    def text(self) -> str:
        """JS-parity alias for ``prompt`` (the JS sibling exposes ``text``)."""
        return self.prompt

    @property
    def risk(self) -> str:
        """JS-parity alias for ``category`` (the JS sibling exposes ``risk``)."""
        return self.category


def load_corpus_from(path: str | Path) -> List[Fixture]:
    """Load and parse a JSON fixture file from an arbitrary path.

    Useful for callers who want to swap in their own corpus shape (tests,
    enterprise rule packs, etc.). The JSON must be a list of objects with
    keys ``id``, ``prompt``/``text``, ``category``/``risk``, ``severity``.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("corpus JSON must be a list of fixture objects")
    out: List[Fixture] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("every corpus entry must be an object")
        prompt = item.get("prompt") or item.get("text")
        category = item.get("category") or item.get("risk")
        if not all(isinstance(v, str) and v for v in (item.get("id"), prompt, category)):
            raise ValueError("every corpus entry needs id, prompt/text, category/risk")
        severity = item.get("severity", "medium")
        if severity not in ("low", "medium", "high"):
            raise ValueError(
                "severity must be 'low', 'medium', or 'high'; got " + repr(severity)
            )
        out.append(
            Fixture(
                id=item["id"],
                prompt=prompt,
                category=category,
                severity=severity,
            )
        )
    return out


def load_corpus() -> List[Fixture]:
    """Return the bundled fixture corpus as a fresh list."""
    return load_corpus_from(_CORPUS_PATH)


# Module-level cache mirrors the JS sibling's exported `fixtures` constant.
fixtures: List[Fixture] = load_corpus()


def get_jailbreak_fixtures(
    *,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    risk: Optional[str] = None,
) -> List[Fixture]:
    """Return fixtures filtered by ``category`` and/or ``severity``.

    ``risk=`` is an alias for ``category=`` to match the JS sibling's option
    name. Filters AND together; ``None`` means "don't filter on this axis".
    """
    cat = category if category is not None else risk
    if cat is not None and severity is None:
        return [f for f in fixtures if f.category == cat]
    if cat is None and severity is not None:
        return [f for f in fixtures if f.severity == severity]
    if cat is not None and severity is not None:
        return [f for f in fixtures if f.category == cat and f.severity == severity]
    return list(fixtures)


def fixture_texts(
    *,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    risk: Optional[str] = None,
) -> List[str]:
    """Same filters as :func:`get_jailbreak_fixtures`, returns prompt strings."""
    return [f.prompt for f in get_jailbreak_fixtures(
        category=category, severity=severity, risk=risk,
    )]
