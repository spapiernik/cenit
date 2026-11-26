"""Generate the compiled CENIT data module from the versioned JSON source."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "current" / "cenit.json"
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
    ("seped", "seped"),
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def date_expression(value: date | None) -> str:
    if value is None:
        return "None"
    return f"date({value.year}, {value.month}, {value.day})"


def parse_operation_start(value: str) -> tuple[date | None, str]:
    label = str(value).strip()
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", label)
    if match is None:
        return None, label
    day, month, year = (int(part) for part in match.groups())
    return date(year, month, day), label


def parse_boolean(value: str) -> bool:
    if value == "SI":
        return True
    if value == "NO":
        return False
    raise ValueError(f"unknown boolean value: {value!r}")


def parse_lengths(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d{1,2}", value or ""))


def parse_entity_types(record: dict[str, Any]) -> tuple[str, ...]:
    flags = record["tipo_de_entidad"]
    return tuple(
        english
        for spanish, english in ENTITY_TYPES
        if flags.get(spanish)
    )


def render_code(record: dict[str, Any]) -> str:
    account = record["tipo_de_cuenta_y_longitud"]
    deposit = account["depósito_electrónico_o_de_bajo_monto"]
    start_date, start_label = parse_operation_start(record["inicio_de_operación"])
    savings = parse_lengths(account["cuenta_de_ahorros"])
    checking = parse_lengths(account["cuenta_corriente"])
    deposit_lengths = parse_lengths(deposit["longitud"])
    deposit_name = (deposit["nombre"] or "").strip() or None

    lines = [
        "    Code(",
        f"        position={record['posición']!r},",
        f"        participant={record['participante']!r},",
        f"        cenit_code={record['código_cenit']!r},",
        f"        operation_start_date={date_expression(start_date)},",
        f"        operation_start_label={start_label!r},",
        f"        entity_types={parse_entity_types(record)!r},",
        f"        supports_debit_transactions={parse_boolean(record['aplica_transacciones_débito'])!r},",
        "        account_types=AccountTypes(",
        f"            savings_account_lengths={savings!r},",
        f"            checking_account_lengths={checking!r},",
        "        ),",
        f"        electronic_or_low_value_deposit={deposit_name!r},",
        f"        electronic_or_low_value_deposit_lengths={deposit_lengths!r},",
        "    ),",
    ]
    return "\n".join(lines)


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
    codes = "\n".join(render_code(record) for record in dataset["participants"])
    entity_totals = "\n".join(
        f"        {english!r}: {int(totals['tipo_de_entidad'][spanish])},"
        for spanish, english in ENTITY_TYPES
    )

    return f'''"""Generated data for cenit. Regenerate with scripts/generate_data.py."""

from __future__ import annotations

from datetime import date
from types import MappingProxyType
from typing import Mapping

from cenit._types import AccountTypes, Code, Totals, normalize_name

SCHEMA_VERSION = {SCHEMA_VERSION}
VERSION = {version!r}
SOURCE_DATE = {date_expression(date.fromisoformat(document_date))}
SOURCE_SHA256 = {source["sha256"]!r}
SOURCE_URL = {source["url"]!r}
SOURCE_FETCHED_AT = {source["fetched_at"]!r}

CODES: tuple[Code, ...] = (
{codes}
)

CODES_BY_CENIT_CODE: Mapping[str, Code] = MappingProxyType(
    {{code.cenit_code: code for code in CODES}}
)
CODES_BY_NAME: Mapping[str, Code] = MappingProxyType(
    {{normalize_name(code.participant): code for code in CODES}}
)
TOTALS = Totals(
    participants={int(totals["participantes"])},
    entity_types=MappingProxyType(
        {{
{entity_totals}
        }}
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
