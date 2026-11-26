"""Versioned CENIT compensation codes.

Each release bundles one immutable snapshot of the official Banrep table. The
data is compiled into the package, so lookups are pure, offline and
deterministic. Publishing a new package version is how new data is released.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from . import _data
from ._types import (
    ENTITY_TYPES,
    AccountCapabilities,
    AccountNumberLengthScope,
    AccountNumberLengthVariant,
    AccountType,
    Code,
    EntityTypeTotals,
    ParticipantRecord,
    Totals,
    normalize_name,
)

__all__ = [
    "ENTITY_TYPES",
    "AccountCapabilities",
    "AccountNumberLengthScope",
    "AccountNumberLengthVariant",
    "AccountType",
    "Code",
    "EntityTypeTotals",
    "ParticipantRecord",
    "Totals",
    "all_records",
    "footnotes",
    "get_account_capabilities",
    "get_by_code",
    "get_by_code_or_raise",
    "get_by_name",
    "is_valid_account_number_length",
    "list_account_number_lengths",
    "list_debit_capable_participants",
    "list_participants_by_entity_type",
    "routing_code",
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


def _account_type(value: AccountType | str) -> AccountType:
    if isinstance(value, AccountType):
        return value
    text = str(value).strip().lower().replace("-", "_")
    aliases = {
        "savings": AccountType.SAVINGS,
        "savings_account": AccountType.SAVINGS,
        "savings_account_number_lengths": AccountType.SAVINGS,
        "checking": AccountType.CHECKING,
        "checking_account": AccountType.CHECKING,
        "checking_account_number_lengths": AccountType.CHECKING,
        "electronic": AccountType.ELECTRONIC_OR_LOW_VALUE_DEPOSIT,
        "electronic_deposit": AccountType.ELECTRONIC_OR_LOW_VALUE_DEPOSIT,
        "electronic_or_low_value_deposit": AccountType.ELECTRONIC_OR_LOW_VALUE_DEPOSIT,
        "electronic_or_low_value_deposit_number_lengths": (
            AccountType.ELECTRONIC_OR_LOW_VALUE_DEPOSIT
        ),
    }
    if text in aliases:
        return aliases[text]
    try:
        return AccountType(text)
    except ValueError:
        raise ValueError(f"unknown account type: {value!r}") from None


def _scope(value: AccountNumberLengthScope | str | None) -> AccountNumberLengthScope | None:
    if value is None:
        return None
    if isinstance(value, AccountNumberLengthScope):
        return value
    try:
        return AccountNumberLengthScope(str(value).strip().lower().replace("-", "_"))
    except ValueError:
        raise ValueError(f"unknown account number length scope: {value!r}") from None


def get_by_code(code: str | int) -> ParticipantRecord | None:
    """Return the record for a four-digit CENIT code, or None if unknown."""
    return _data.CODES_BY_CENIT_CODE.get(_code_text(code))


def get_by_code_or_raise(code: str | int) -> ParticipantRecord:
    """Return the record for a four-digit CENIT code, raising KeyError if unknown."""
    key = _code_text(code)
    try:
        return _data.CODES_BY_CENIT_CODE[key]
    except KeyError:
        raise KeyError(f"unknown CENIT code: {code!r}") from None


def get_by_name(name: str) -> ParticipantRecord | None:
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


def all_records() -> tuple[ParticipantRecord, ...]:
    """Return every record in table order."""
    return _data.RECORDS


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


def footnotes() -> Mapping[str, str]:
    """Return the official footnote markers and their English meanings."""
    return _data.FOOTNOTES


def get_account_capabilities(code: str | int) -> AccountCapabilities | None:
    """Return the qualified account capabilities for a CENIT code."""
    record = get_by_code(code)
    return record.account_capabilities if record is not None else None


def list_account_number_lengths(
    code: str | int,
    account_type: AccountType | str,
    scope: AccountNumberLengthScope | str | None = None,
) -> tuple[int, ...]:
    """Return accepted account number lengths, optionally filtered by scope."""
    capabilities = get_account_capabilities(code)
    if capabilities is None:
        return ()

    selected = capabilities.for_account_type(_account_type(account_type))
    wanted = _scope(scope)
    lengths: list[int] = []
    for variant in selected:
        if wanted is None or variant.scope == wanted:
            lengths.extend(variant.lengths)
    return tuple(lengths)


def is_valid_account_number_length(
    code: str | int,
    account_type: AccountType | str,
    length: int,
    scope: AccountNumberLengthScope | str = AccountNumberLengthScope.STANDARD,
) -> bool:
    """Check an account number length for one account type and scope."""
    target = int(length)
    wanted = _scope(scope)
    if wanted is None:
        raise ValueError("scope cannot be None")
    return target in list_account_number_lengths(code, account_type, wanted)


def list_participants_by_entity_type(entity_type: str) -> tuple[ParticipantRecord, ...]:
    """Return every participant with the given English entity type."""
    key = str(entity_type).strip().lower()
    if key not in ENTITY_TYPES:
        raise ValueError(f"unknown entity type: {entity_type!r}")
    return tuple(record for record in _data.RECORDS if key in record.entity_types)


def list_debit_capable_participants() -> tuple[ParticipantRecord, ...]:
    """Return every participant that supports debit transactions."""
    return tuple(record for record in _data.RECORDS if record.supports_debit_transactions)


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
