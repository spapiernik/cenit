"""Versioned CENIT compensation codes.

Each release bundles one immutable snapshot of the official Banrep table. The
data is compiled into the package, so lookups are pure, offline and
deterministic. Publishing a new package version is how new data is released.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import TypeVar, overload

from rapidfuzz import distance, fuzz

from . import _data
from ._types import (
    AccountNumberLengthScope,
    AccountType,
    EntityType,
    Participant,
    Source,
    Totals,
    normalize_name,
)
from .view import footnote_definitions

_MISSING = object()
_T = TypeVar("_T")


class ParticipantNotFound(KeyError):
    """Raised when a lookup finds no matching participant."""


__all__ = [
    "AccountNumberLengthScope",
    "AccountType",
    "EntityType",
    "Participant",
    "ParticipantNotFound",
    "all_records",
    "footnote_definitions",
    "footnotes",
    "get_by_code",
    "get_by_name",
    "list_debit_capable_participants",
    "list_participants_by_entity_type",
    "source",
    "totals",
    "version"
]


def _code_text(code: str | int) -> str:
    if isinstance(code, bool):
        raise TypeError("code must be a string or integer, not bool")
    if isinstance(code, int):
        return str(code)
    if isinstance(code, str):
        return code.strip()
    raise TypeError("code must be a string or integer")


def _jaro_winkler(left: str, right: str) -> float:
    return distance.JaroWinkler.similarity(left, right) * 100


def _best_name_match(
    key: str, scorer: Callable[[str, str], float], cutoff: float
) -> Participant | None:
    best_score = -1.0
    best_row = 0
    best: Participant | None = None
    for normalized, record in _data.CODES_BY_NAME.items():
        score = scorer(key, normalized)
        if score < cutoff:
            continue
        if score > best_score or (score == best_score and record.row_number < best_row):
            best_score = score
            best_row = record.row_number
            best = record
    return best


@overload
def get_by_code(code: str | int) -> Participant: ...


@overload
def get_by_code(code: str | int, default: _T) -> Participant | _T: ...


def get_by_code(code: str | int, default: object = _MISSING) -> Participant | object:
    """Return the record for a CENIT code, raising unless a default is given."""
    record = _data.CODES_BY_CENIT_CODE.get(_code_text(code))
    if record is None:
        if default is not _MISSING:
            return default
        raise ParticipantNotFound(f"unknown CENIT code: {code!r}")
    return record


@overload
def get_by_name(name: str) -> Participant: ...


@overload
def get_by_name(name: str, default: _T) -> Participant | _T: ...


def get_by_name(name: str, default: object = _MISSING) -> Participant | object:
    """Return the closest normalized name match, raising unless a default is given."""
    key = normalize_name(name)
    record = _data.CODES_BY_NAME.get(key)
    if record is None and key:
        record = _best_name_match(key, fuzz.WRatio, 90)
    if record is None and len(key) >= 4:
        record = _best_name_match(key, _jaro_winkler, 69)
    if record is None:
        if default is not _MISSING:
            return default
        raise ParticipantNotFound(f"unknown participant name: {name!r}")
    return record


def all_records() -> tuple[Participant, ...]:
    """Return every record in table order."""
    return _data.RECORDS


def footnotes() -> Mapping[str, str]:
    """Return the official footnote markers and their English meanings."""
    return _data.FOOTNOTES


def list_participants_by_entity_type(entity_type: str | EntityType) -> tuple[Participant, ...]:
    """Return every participant with the given English entity type."""
    try:
        wanted = EntityType(entity_type)
    except ValueError:
        raise ValueError(f"unknown entity type: {entity_type!r}") from None
    return tuple(record for record in _data.RECORDS if wanted in record.entity_types)


def list_debit_capable_participants() -> tuple[Participant, ...]:
    """Return every participant that supports debit transactions."""
    return tuple(record for record in _data.RECORDS if record.supports_debit_transactions)


def totals() -> Totals:
    """Return the totals row bundled with this release."""
    return _data.TOTALS


def version() -> str:
    """Return the package version that defines this dataset snapshot."""
    return _data.VERSION


def source() -> Source:
    """Return the provenance of this dataset snapshot."""
    return Source(
        url=_data.SOURCE_URL,
        sha256=_data.SOURCE_SHA256,
        document_date=_data.SOURCE_DATE,
        fetched_at=datetime.fromisoformat(_data.SOURCE_FETCHED_AT),
        schema_version=_data.SCHEMA_VERSION,
    )
