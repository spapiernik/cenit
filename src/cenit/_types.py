"""Public data types for the CENIT library."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Mapping

ENTITY_TYPES = (
    "bank",
    "financial_cooperative",
    "financial_corporation",
    "financing_company",
    "government_entity",
    "information_operator",
    "seped",
)


@dataclass(frozen=True, slots=True)
class AccountTypes:
    """Account lengths for one participant."""

    savings_account_lengths: tuple[int, ...]
    checking_account_lengths: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Code:
    """One participant row from the versioned CENIT table."""

    position: int
    participant: str
    cenit_code: str
    operation_start_date: date | None
    operation_start_label: str
    entity_types: tuple[str, ...]
    supports_debit_transactions: bool
    account_types: AccountTypes
    electronic_or_low_value_deposit: str | None
    electronic_or_low_value_deposit_lengths: tuple[int, ...]

    @property
    def participant_code(self) -> str:
        """Return the three-digit participant part of the CENIT code."""
        return self.cenit_code[1:]

    @property
    def routing_code(self) -> str:
        """Return the four-digit routing code."""
        return "1" + self.participant_code


@dataclass(frozen=True, slots=True)
class Totals:
    """Totals row from the versioned CENIT table."""

    participants: int
    entity_types: Mapping[str, int]


def normalize_name(value: str) -> str:
    """Return an accent-insensitive comparison key for a participant name."""
    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).split())
