"""Generate the compiled CENIT data module from the versioned JSON source."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tomllib
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "current" / "cenit.json"
CSV_PATH = ROOT / "data" / "current" / "cenit.csv"
SOURCE_PATH = ROOT / "data" / "source.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"
MODULE_PATH = ROOT / "src" / "cenit" / "_data.py"

SCHEMA_VERSION = 2
ENTITY_TYPES = (
    ("bancos", "bank"),
    ("cooperativa_financiera", "financial_cooperative"),
    ("corporación_financiera", "financial_corporation"),
    ("compañía_de_financiamiento", "financing_company"),
    ("entidad_del_estado", "government_entity"),
    ("operador_de_información", "information_operator"),
    ("sedpe", "sedpe"),
)
ENTITY_TYPE_ALIASES = {"seped": "sedpe", "sedpe": "sedpe"}
FOOTNOTES = {
    "(*)": "Linked before May 2025",
    "(**)": "Used for special collection agreements",
    "(***)": "Includes leading zeros",
    "(****)": "Electronic deposit service available but not enabled in CENIT",
}
MARKER_SCOPES = {
    "*": "LINKED_BEFORE_MAY_2025",
    "**": "SPECIAL_COLLECTION_AGREEMENT",
    "***": "INCLUDES_LEADING_ZEROS",
    "****": "ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT",
}
LENGTH_TOKEN = re.compile(
    r"\((?P<parenthesized>[^)]*)\)(?P<parenthesized_markers>\*{1,4})?"
    r"|(?P<plain>\d+(?:\s*(?:,|y)\s*\d+)*)(?P<plain_markers>\*{1,4})?",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def date_expression(value: date | None) -> str:
    if value is None:
        return "None"
    return f"date({value.year}, {value.month}, {value.day})"


def parse_operation_start(value: str) -> tuple[date | None, str | None]:
    label = str(value).strip()
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", label)
    if match is None:
        return None, label or None
    day, month, year = (int(part) for part in match.groups())
    return date(year, month, day), None


def parse_boolean(value: str) -> bool:
    if value == "SI":
        return True
    if value == "NO":
        return False
    raise ValueError(f"unknown boolean value: {value!r}")


def parse_length_variants(value: str) -> tuple[tuple[tuple[int, ...], str], ...]:
    variants: list[tuple[tuple[int, ...], str]] = []
    for match in LENGTH_TOKEN.finditer(value or ""):
        parenthesized = match.group("parenthesized")
        if parenthesized is not None:
            trailing = match.group("parenthesized_markers") or ""
            if trailing:
                markers = trailing
                lengths_text = parenthesized
            elif parenthesized and all(char == "*" for char in parenthesized):
                markers = parenthesized
                lengths_text = ""
            else:
                markers = ""
                lengths_text = parenthesized
        else:
            markers = match.group("plain_markers") or ""
            lengths_text = match.group("plain") or ""

        markers = "*" * len(markers) if markers else ""
        lengths = tuple(int(part) for part in re.findall(r"\d+", lengths_text))
        if not lengths and not markers:
            continue
        if markers and markers not in MARKER_SCOPES:
            raise ValueError(f"unknown footnote markers: {markers!r}")
        variants.append((lengths, markers))
    return tuple(variants)


def canonicalize_entity_type_key(key: str) -> str:
    normalized = str(key).strip().lower()
    return ENTITY_TYPE_ALIASES.get(normalized, normalized)


def entity_types_expression(record: dict[str, Any]) -> str:
    flags = {
        canonicalize_entity_type_key(key): value
        for key, value in record["tipo_de_entidad"].items()
    }
    members = [
        f"EntityType.{english.upper()}"
        for spanish, english in ENTITY_TYPES
        if flags.get(spanish)
    ]
    suffix = "," if len(members) == 1 else ""
    return "(" + ", ".join(members) + suffix + ")"


def scope_expression(markers: str) -> str:
    if not markers:
        return "AccountNumberLengthScope.STANDARD"
    return f"AccountNumberLengthScope.{MARKER_SCOPES[markers]}"


def render_variants(
    variants: tuple[tuple[tuple[int, ...], str], ...], indent: int
) -> str:
    if not variants:
        return "()"
    pad = " " * indent
    lines = ["("]
    for lengths, markers in variants:
        marker_value = (markers,) if markers else ()
        lines.append(f"{pad}    AccountNumberLengthVariant(")
        lines.append(f"{pad}        lengths={lengths!r},")
        lines.append(f"{pad}        footnote_markers={marker_value!r},")
        lines.append(f"{pad}        scope={scope_expression(markers)},")
        lines.append(f"{pad}    ),")
    lines.append(f"{pad})")
    return "\n".join(lines)


def collect_footnotes(
    note: str | None,
    groups: tuple[tuple[tuple[tuple[int, ...], str], ...], ...],
) -> tuple[str, ...]:
    candidates: list[str] = []
    if note:
        candidates.append(note)
    for variants in groups:
        for _, markers in variants:
            if markers:
                candidates.append(f"({markers})")
    result: list[str] = []
    for candidate in candidates:
        if candidate in FOOTNOTES and candidate not in result:
            result.append(candidate)
    return tuple(result)


def render_participant(record: dict[str, Any]) -> str:
    account = record["tipo_de_cuenta_y_longitud"]
    deposit = account["depósito_electrónico_o_de_bajo_monto"]
    start_date, start_note = parse_operation_start(record["inicio_de_operación"])
    savings = parse_length_variants(account["cuenta_de_ahorros"])
    checking = parse_length_variants(account["cuenta_corriente"])
    deposit_variants = parse_length_variants(deposit["longitud"])
    deposit_name = (deposit["nombre"] or "").strip() or None
    footnotes = collect_footnotes(start_note, (savings, checking, deposit_variants))

    lines = [
        "    Participant(",
        f"        row_number={record['posición']!r},",
        f"        name={record['participante']!r},",
        f"        code={record['código_cenit']!r},",
        f"        operation_start_date={date_expression(start_date)},",
        f"        operation_start_note={start_note!r},",
        f"        entity_types={entity_types_expression(record)},",
        f"        supports_debit_transactions={parse_boolean(record['aplica_transacciones_débito'])!r},",
        "        account_capabilities=AccountCapabilities(",
        f"            savings_account_number_lengths={render_variants(savings, 16)},",
        f"            checking_account_number_lengths={render_variants(checking, 16)},",
        "            electronic_or_low_value_deposit_number_lengths="
        f"{render_variants(deposit_variants, 16)},",
        "        ),",
        f"        electronic_or_low_value_deposit_name={deposit_name!r},",
        f"        footnotes={footnotes!r},",
        "    ),",
    ]
    return "\n".join(lines)


def csv_lines_expression(dataset: dict[str, Any]) -> str:
    lines = CSV_PATH.read_text(encoding="utf-8-sig").splitlines()
    pairs = [
        (row, line)
        for row, line in zip(csv.DictReader(lines), lines[1:])
        if not row["participante"].strip().lower().startswith("total participantes")
    ]
    if len(pairs) != len(dataset["participants"]):
        raise ValueError("CSV participant row count does not match the dataset")
    entries = [
        f"    {row['código_cenit']!r}: {line!r}," for row, line in pairs
    ]
    return "\n".join(entries)


def render_module(dataset: dict[str, Any], source: dict[str, Any], version: str) -> str:
    if dataset["schema_version"] != SCHEMA_VERSION:
        raise ValueError("dataset schema version does not match the generator")
    if source["schema_version"] != SCHEMA_VERSION:
        raise ValueError("source schema version does not match the generator")
    if dataset["source"]["sha256"] != source["sha256"]:
        raise ValueError("dataset checksum does not match data/source.json")

    document_date = source.get("document_date")
    if not document_date:
        raise ValueError("data/source.json has no document_date")

    totals = dataset["totals"]
    participants = "\n".join(
        render_participant(record) for record in dataset["participants"]
    )
    entity_totals_by_key = {
        canonicalize_entity_type_key(key): value
        for key, value in totals["tipo_de_entidad"].items()
    }
    entity_totals = "\n".join(
        f"        {english}={int(entity_totals_by_key[spanish])},"
        for spanish, english in ENTITY_TYPES
    )
    footnotes = "\n".join(
        f"    {marker!r}: {meaning!r}," for marker, meaning in FOOTNOTES.items()
    )
    csv_lines = csv_lines_expression(dataset)

    return f'''"""Generated data for cenit. Regenerate with scripts/generate_data.py."""

from __future__ import annotations

from datetime import date
from types import MappingProxyType
from typing import Mapping

from cenit._types import (
    AccountCapabilities,
    AccountNumberLengthScope,
    AccountNumberLengthVariant,
    EntityType,
    EntityTypeTotals,
    Participant,
    Totals,
    normalize_name,
)

SCHEMA_VERSION = {SCHEMA_VERSION}
VERSION = {version!r}
SOURCE_DATE = {date_expression(date.fromisoformat(document_date))}
SOURCE_SHA256 = {source["sha256"]!r}
SOURCE_URL = {source["url"]!r}
SOURCE_FETCHED_AT = {source["fetched_at"]!r}

FOOTNOTES: Mapping[str, str] = MappingProxyType(
{{
{footnotes}
}}
)

CSV_LINES: Mapping[str, str] = MappingProxyType(
{{
{csv_lines}
}}
)

RECORDS: tuple[Participant, ...] = (
{participants}
)

CODES_BY_CENIT_CODE: Mapping[str, Participant] = MappingProxyType(
    {{record.code: record for record in RECORDS}}
)
CODES_BY_NAME: Mapping[str, Participant] = MappingProxyType(
    {{normalize_name(record.name): record for record in RECORDS}}
)
TOTALS = Totals(
    participants={int(totals["participantes"])},
    entity_types=EntityTypeTotals(
{entity_totals}
    ),
)
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that the generated module is current without writing it",
    )
    args = parser.parse_args(argv)

    dataset = read_json(DATA_PATH)
    source = read_json(SOURCE_PATH)
    version = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))["project"]["version"]
    generated = render_module(dataset, source, version)

    if args.check:
        if MODULE_PATH.read_text(encoding="utf-8") != generated:
            print(f"ERROR: {MODULE_PATH} is out of date", file=sys.stderr)
            return 1
        print(f"OK: {MODULE_PATH} is current")
        return 0

    if MODULE_PATH.exists() and MODULE_PATH.read_text(encoding="utf-8") == generated:
        print(f"Unchanged: {MODULE_PATH}")
        return 0

    MODULE_PATH.write_text(generated, encoding="utf-8")
    print(f"Wrote: {MODULE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
