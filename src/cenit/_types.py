"""Public data types for the CENIT library."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

ENTITY_TYPES = (
    "bank",
    "financial_cooperative",
    "financial_corporation",
    "financing_company",
    "government_entity",
    "information_operator",
    "seped",
)


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


@dataclass(frozen=True, slots=True)
class AccountNumberLengthVariant:
    """A source group of account number lengths with its footnote qualifiers."""

    lengths: tuple[int, ...]
    footnote_markers: tuple[str, ...] = ()
    scope: AccountNumberLengthScope = AccountNumberLengthScope.STANDARD

    def __str__(self) -> str:
        return ", ".join(str(length) for length in self.lengths)


@dataclass(frozen=True, slots=True)
class AccountCapabilities:
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
        key = AccountType(account_type)
        if key is AccountType.SAVINGS:
            return self.savings_account_number_lengths
        if key is AccountType.CHECKING:
            return self.checking_account_number_lengths
        return self.electronic_or_low_value_deposit_number_lengths


@dataclass(frozen=True, slots=True)
class ParticipantRecord:
    """One participant row from the versioned CENIT table."""

    row_number: int
    participant_name: str
    cenit_code: str
    operation_start_date: date | None
    operation_start_note: str | None
    entity_types: tuple[str, ...]
    supports_debit_transactions: bool
    account_capabilities: AccountCapabilities
    electronic_or_low_value_deposit_name: str | None
    footnotes: tuple[str, ...] = ()

    @property
    def participant_code(self) -> str:
        """Return the three-digit participant part of the CENIT code."""
        return self.cenit_code[1:]

    @property
    def routing_code(self) -> str:
        """Return the four-digit routing code."""
        return "1" + self.participant_code


Code = ParticipantRecord


@dataclass(frozen=True, slots=True)
class EntityTypeTotals:
    """Counts by entity type from the totals row."""

    bank: int
    financial_cooperative: int
    financial_corporation: int
    financing_company: int
    government_entity: int
    information_operator: int
    seped: int


@dataclass(frozen=True, slots=True)
class Totals:
    """Totals row from the versioned CENIT table."""

    participants: int
    entity_types: EntityTypeTotals


def normalize_name(value: str) -> str:
    """Return an accent-insensitive comparison key for a participant name."""
    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).split())
