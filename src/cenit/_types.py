"""Public data types for the CENIT library."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

class EntityType(StrEnum):
    BANK = "bank"
    FINANCIAL_COOPERATIVE = "financial_cooperative"
    FINANCIAL_CORPORATION = "financial_corporation"
    FINANCING_COMPANY = "financing_company"
    GOVERNMENT_ENTITY = "government_entity"
    INFORMATION_OPERATOR = "information_operator"
    SEDPE = "sedpe"

    @classmethod
    def _missing_(cls, value: object) -> EntityType | None:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "seped":
                return cls.SEDPE
            for member in cls:
                if member.value == normalized:
                    return member
        return None


class _RichViewMixin:
    __slots__ = ()

    def __rich_console__(self, console, options):
        from .view import render

        yield render(self)


class AccountType(StrEnum):
    SAVINGS = "savings"
    CHECKING = "checking"
    ELECTRONIC_OR_LOW_VALUE_DEPOSIT = "electronic_or_low_value_deposit"


class AccountNumberLengthScope(StrEnum):
    STANDARD = "standard"
    SPECIAL_COLLECTION_AGREEMENT = "special_collection_agreement"
    INCLUDES_LEADING_ZEROS = "includes_leading_zeros"
    ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT = "electronic_deposit_not_enabled_in_cenit"
    LINKED_BEFORE_MAY_2025 = "linked_before_may_2025"


def _coerce_account_type(value: AccountType | str) -> AccountType:
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


def _coerce_scope(
    value: AccountNumberLengthScope | str | None,
) -> AccountNumberLengthScope | None:
    if value is None:
        return None
    if isinstance(value, AccountNumberLengthScope):
        return value
    try:
        return AccountNumberLengthScope(str(value).strip().lower().replace("-", "_"))
    except ValueError:
        raise ValueError(f"unknown account number length scope: {value!r}") from None


@dataclass(frozen=True, slots=True)
class AccountNumberLengthVariant(_RichViewMixin):
    """A source group of account number lengths with its footnote qualifiers."""

    lengths: tuple[int, ...]
    footnote_markers: tuple[str, ...] = ()
    scope: AccountNumberLengthScope = AccountNumberLengthScope.STANDARD

    def __str__(self) -> str:
        return ", ".join(str(length) for length in self.lengths)


@dataclass(frozen=True, slots=True)
class AccountCapabilities(_RichViewMixin):
    """Qualified account number lengths accepted by one participant."""

    savings_account_number_lengths: tuple[AccountNumberLengthVariant, ...] = ()
    checking_account_number_lengths: tuple[AccountNumberLengthVariant, ...] = ()
    electronic_or_low_value_deposit_number_lengths: tuple[
        AccountNumberLengthVariant, ...
    ] = ()

    def for_account_type(
        self, account_type: AccountType | str
    ) -> tuple[AccountNumberLengthVariant, ...]:
        """Return the variants for one account type."""
        key = _coerce_account_type(account_type)
        if key is AccountType.SAVINGS:
            return self.savings_account_number_lengths
        if key is AccountType.CHECKING:
            return self.checking_account_number_lengths
        return self.electronic_or_low_value_deposit_number_lengths


@dataclass(frozen=True, slots=True)
class Participant(_RichViewMixin):
    """One participant row from the versioned CENIT table."""

    row_number: int
    name: str
    code: str
    operation_start_date: date | None
    operation_start_note: str | None
    entity_types: tuple[EntityType, ...]
    supports_debit_transactions: bool
    account_capabilities: AccountCapabilities
    electronic_or_low_value_deposit_name: str | None
    footnotes: tuple[str, ...] = ()

    def account_number_lengths(
        self,
        account_type: AccountType | str,
        scope: AccountNumberLengthScope | str | None = AccountNumberLengthScope.STANDARD,
    ) -> tuple[int, ...]:
        """Return accepted lengths for one account type and scope."""
        selected = self.account_capabilities.for_account_type(account_type)
        wanted = _coerce_scope(scope)
        lengths: list[int] = []
        for variant in selected:
            if wanted is None or variant.scope == wanted:
                lengths.extend(variant.lengths)
        return tuple(lengths)

    def supports_account_number_length(
        self,
        account_type: AccountType | str,
        length: int,
        scope: AccountNumberLengthScope | str | None = AccountNumberLengthScope.STANDARD,
    ) -> bool:
        """Check whether one account number length is accepted."""
        return int(length) in self.account_number_lengths(account_type, scope)


@dataclass(frozen=True, slots=True)
class EntityTypeTotals(_RichViewMixin):
    """Counts by entity type from the totals row."""

    bank: int
    financial_cooperative: int
    financial_corporation: int
    financing_company: int
    government_entity: int
    information_operator: int
    sedpe: int


@dataclass(frozen=True, slots=True)
class Totals(_RichViewMixin):
    """Totals row from the versioned CENIT table."""

    participants: int
    entity_types: EntityTypeTotals


def normalize_name(value: str) -> str:
    """Return an accent-insensitive comparison key for a participant name."""
    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).split())
