"""Versioned CENIT compensation codes.

Each release bundles one immutable snapshot of the official Banrep table. The
data is compiled into the package, so lookups are pure, offline and
deterministic. Publishing a new package version is how new data is released.
"""

from __future__ import annotations

from datetime import date

from . import _data
from ._types import ENTITY_TYPES, AccountTypes, Code, Totals, normalize_name

__all__ = [
    "ENTITY_TYPES",
    "AccountTypes",
    "Code",
    "Totals",
    "all_records",
    "get_by_name",
    "get_by_code",
    "schema_version",
    "source_date",
    "source_fetched_at",
    "source_sha256",
    "source_url",
    "totals",
    "version",
]

SCHEMA_VERSION = _data.SCHEMA_VERSION


def _code_text(code: str | int) -> str:
    if isinstance(code, bool):
        raise TypeError("code must be a string or integer, not bool")
    if isinstance(code, int):
        return str(code)
    if isinstance(code, str):
        return code.strip()
    raise TypeError("code must be a string or integer")


def get_by_code(code: str | int) -> Code | None:
    """Return the record for a four-digit CENIT code, or None if unknown."""
    return _data.CODES_BY_CENIT_CODE.get(_code_text(code))


def get_by_code_or_raise(code: str | int) -> Code:
    """Return the record for a four-digit CENIT code, raising KeyError if unknown."""
    key = _code_text(code)
    try:
        return _data.CODES_BY_CENIT_CODE[key]
    except KeyError:
        raise KeyError(f"unknown CENIT code: {code!r}") from None


def get_by_name(name: str) -> Code | None:
    """Find a participant by accent-insensitive exact or unique partial name."""
    key = normalize_name(name)
    record = _data.CODES_BY_NAME.get(key)
    if record is not None:
        return record
    matches = [
        candidate
        for normalized, candidate in _data.CODES_BY_NAME.items()
        if key and key in normalized
    ]
    return matches[0] if len(matches) >= 1 else None

def all_records() -> tuple[Code, ...]:
    """Return every record in table order."""
    return _data.CODES

def routing_code(code: str | int) -> str | None:
    """Return the four-digit routing code for a known participant.

    Accepts either a full CENIT code such as "1007" or a three-digit
    participant code such as "007". The routing code is "1" followed by the
    three-digit participant code.
    """
    key = _code_text(code)
    if len(key) == 3 and key.isdigit():
        key = "1" + key
    record = _data.CODES_BY_CENIT_CODE.get(key)
    return record.routing_code if record is not None else None


def totals() -> Totals:
    """Return the totals row bundled with this release."""
    return _data.TOTALS


def version() -> str:
    """Return the package version that defines this dataset snapshot."""
    return _data.VERSION


def schema_version() -> int:
    """Return the data schema version."""
    return _data.SCHEMA_VERSION


def source_date() -> date:
    """Return the official document date represented by this release."""
    return _data.SOURCE_DATE


def source_fetched_at() -> str:
    """Return when the source PDF was fetched during data generation."""
    return _data.SOURCE_FETCHED_AT


def source_sha256() -> str:
    """Return the checksum of the source PDF used by this release."""
    return _data.SOURCE_SHA256


def source_url() -> str:
    """Return the official source URL recorded for this release."""
    return _data.SOURCE_URL
