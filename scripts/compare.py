"""Compare two extracted CENIT datasets semantically."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from cenit.view import ENTITY_TYPE_LABELS, LABELS
from generate_data import ENTITY_TYPES

EXCLUDED_PARTICIPANT_FIELDS = {"posición"}

EN_LABELS = LABELS["en"]
ENTITY_KEYS = dict(ENTITY_TYPES)

FIELD_LABELS = {
    "participante": EN_LABELS["name"],
    "código_cenit": EN_LABELS["code"],
    "inicio_de_operación": EN_LABELS["operation_start_date"],
    "tipo_de_entidad": EN_LABELS["entity_types"],
    "aplica_transacciones_débito": EN_LABELS["supports_debit_transactions"],
    "tipo_de_cuenta_y_longitud": EN_LABELS["account_capabilities"],
    "participantes": EN_LABELS["participants"],
}

ACCOUNT_FIELD_LABELS = {
    "cuenta_de_ahorros": EN_LABELS["savings_account_number_lengths"],
    "cuenta_corriente": EN_LABELS["checking_account_number_lengths"],
    "depósito_electrónico_o_de_bajo_monto": EN_LABELS[
        "electronic_or_low_value_deposit_number_lengths"
    ],
    "longitud": EN_LABELS["lengths"],
}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value} if prefix else {}
    flattened: dict[str, Any] = {}
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, dict) and item:
            flattened.update(flatten(item, path))
        else:
            flattened[path] = item
    return flattened


def participant_index(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        code = str(record.get("código_cenit") or f"row-{record.get('posición', '?')}")
        index[code] = record
    return index


def field_changes(before: Any, after: Any) -> list[dict[str, Any]]:
    before_flat = flatten(before)
    after_flat = flatten(after)
    changes = []
    for path in sorted(before_flat.keys() | after_flat.keys()):
        if path in EXCLUDED_PARTICIPANT_FIELDS:
            continue
        old = before_flat.get(path)
        new = after_flat.get(path)
        if old != new:
            changes.append({"path": path, "before": old, "after": new})
    return changes


def participant_name(record: dict[str, Any]) -> str:
    return str(record.get("participante") or "")


def operation_start(record: dict[str, Any]) -> str:
    return str(record.get("inicio_de_operación") or "")


def entity_types(record: dict[str, Any]) -> str:
    flags = record.get("tipo_de_entidad") or {}
    return ", ".join(
        ENTITY_TYPE_LABELS["en"][ENTITY_KEYS[key]]
        for key, value in flags.items()
        if value and key in ENTITY_KEYS
    )


def recent_change_log(
    entries: list[dict[str, Any]], previous_date: str | None
) -> list[dict[str, Any]]:
    if not previous_date:
        return list(entries)
    return [entry for entry in entries if str(entry.get("date", "")) > previous_date]


def compare(
    previous: dict[str, Any],
    current: dict[str, Any],
    previous_report: dict[str, Any] | None = None,
    current_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    previous_records = participant_index(previous.get("participants", []))
    current_records = participant_index(current.get("participants", []))

    added = sorted(current_records.keys() - previous_records.keys())
    removed = sorted(previous_records.keys() - current_records.keys())
    changed = []
    for code in sorted(previous_records.keys() & current_records.keys()):
        changes = field_changes(previous_records[code], current_records[code])
        if changes:
            changed.append(
                {
                    "code": code,
                    "name": participant_name(current_records[code]),
                    "fields": changes,
                }
            )

    totals_changes = field_changes(previous.get("totals", {}), current.get("totals", {}))
    previous_source = previous.get("source") or {}
    current_source = current.get("source") or {}
    report = current_report or {}

    return {
        "changed": bool(added or removed or changed or totals_changes),
        "added": added,
        "removed": removed,
        "added_participants": [
            {
                "code": code,
                "name": participant_name(current_records[code]),
                "start": operation_start(current_records[code]),
                "entity_types": entity_types(current_records[code]),
            }
            for code in added
        ],
        "removed_participants": [
            {
                "code": code,
                "name": participant_name(previous_records[code]),
                "start": operation_start(previous_records[code]),
                "entity_types": entity_types(previous_records[code]),
            }
            for code in removed
        ],
        "changed_participants": changed,
        "totals_changes": totals_changes,
        "previous_participants": len(previous_records),
        "current_participants": len(current_records),
        "previous_source": previous_source,
        "current_source": current_source,
        "change_log": recent_change_log(
            report.get("change_log", []), previous_source.get("document_date")
        ),
    }


def label(path: str) -> str:
    parts = path.split(".")
    if parts[0] == "tipo_de_entidad" and len(parts) > 1:
        key = ENTITY_KEYS.get(parts[1])
        if key is not None:
            return f"{EN_LABELS['entity_types']} / {ENTITY_TYPE_LABELS['en'][key]}"
    if parts[0] == "tipo_de_cuenta_y_longitud":
        if (
            len(parts) == 3
            and parts[1] == "depósito_electrónico_o_de_bajo_monto"
            and parts[2] == "nombre"
        ):
            return (
                f"{EN_LABELS['account_capabilities']} / "
                f"{EN_LABELS['electronic_or_low_value_deposit_name']}"
            )
        account_parts = [
            ACCOUNT_FIELD_LABELS.get(part, part.replace("_", " ").title())
            for part in parts[1:]
        ]
        return " / ".join([EN_LABELS["account_capabilities"], *account_parts])
    return FIELD_LABELS.get(parts[0], parts[0].replace("_", " ").title())


def display(value: Any) -> str:
    if isinstance(value, str):
        return f"`{value}`" if value else "`(empty)`"
    if isinstance(value, bool):
        return "`true`" if value else "`false`"
    if value is None:
        return "`null`"
    return f"`{value}`"


def cell(value: Any) -> str:
    return display(value).replace("|", "\\|")


def text_cell(value: Any) -> str:
    return str(value or "None").replace("|", "\\|")


def format_date(value: str | None) -> str:
    if not value:
        return "unknown"
    try:
        return date.fromisoformat(value).strftime("%d %b %Y")
    except ValueError:
        return str(value)


def render_markdown(result: dict[str, Any]) -> str:
    source = result.get("current_source") or {}
    previous_source = result.get("previous_source") or {}
    url = source.get("url")
    source_link = f"[official PDF]({url})" if url else "official PDF"
    lines = [
        f"# CENIT table sync - {format_date(source.get('document_date'))}",
        "",
        f"Source: {source_link}, "
        f"SHA-256 `{source.get('sha256') or 'unknown'}`.",
        f"Previous snapshot: {format_date(previous_source.get('document_date'))}, "
        f"SHA-256 `{previous_source.get('sha256') or 'unknown'}`.",
        "",
        "| Metric | Before | After |",
        "| --- | ---: | ---: |",
        f"| Participants | {result['previous_participants']} | "
        f"{result['current_participants']} |",
        f"| Added | 0 | {len(result['added'])} |",
        f"| Removed | 0 | {len(result['removed'])} |",
        f"| Changed | 0 | {len(result['changed_participants'])} |",
        "",
    ]

    lines.extend(["## Added Participants", ""])
    if result["added_participants"]:
        lines.extend(
            [
                f"| {EN_LABELS['code']} | {EN_LABELS['name']} | "
                f"{EN_LABELS['operation_start_date']} | {EN_LABELS['entity_types']} |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in result["added_participants"]:
            lines.append(
                f"| {text_cell(item['code'])} | {text_cell(item['name'])} | "
                f"{text_cell(item['start'])} | {text_cell(item['entity_types'])} |"
            )
    else:
        lines.append("None")
    lines.append("")

    lines.extend(["## Removed Participants", ""])
    if result["removed_participants"]:
        lines.extend(
            [
                f"| {EN_LABELS['code']} | {EN_LABELS['name']} | "
                f"{EN_LABELS['operation_start_date']} | {EN_LABELS['entity_types']} |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in result["removed_participants"]:
            lines.append(
                f"| {text_cell(item['code'])} | {text_cell(item['name'])} | "
                f"{text_cell(item['start'])} | {text_cell(item['entity_types'])} |"
            )
    else:
        lines.append("None")
    lines.append("")

    changed_rows = [
        (entry, field)
        for entry in result["changed_participants"]
        for field in entry["fields"]
    ]
    lines.extend(["## Changed Participants", ""])
    if changed_rows:
        if len(changed_rows) > 10:
            lines.extend(
                ["<details>", f"<summary>Show {len(changed_rows)} field changes</summary>", ""]
            )
        lines.extend(
            [
                f"| {EN_LABELS['code']} | {EN_LABELS['name']} | "
                f"{EN_LABELS['field']} | Before | After |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for entry, field in changed_rows:
            lines.append(
                f"| {text_cell(entry['code'])} | {text_cell(entry['name'])} | "
                f"{text_cell(label(field['path']))} | {cell(field['before'])} | "
                f"{cell(field['after'])} |"
            )
        if len(changed_rows) > 10:
            lines.extend(["", "</details>"])
    else:
        lines.append("None")
    lines.append("")

    lines.extend(["## Totals", ""])
    if result["totals_changes"]:
        lines.extend(
            [f"| {EN_LABELS['field']} | Before | After |", "| --- | --- | --- |"]
        )
        for field in result["totals_changes"]:
            lines.append(
                f"| {text_cell(label(field['path']))} | {cell(field['before'])} | "
                f"{cell(field['after'])} |"
            )
    else:
        lines.append("No changes")
    lines.append("")

    lines.extend(["## Official Change Log", ""])
    if result["change_log"]:
        for entry in result["change_log"]:
            lines.append(
                f"> {format_date(entry.get('date'))}: "
                f"{str(entry.get('text', '')).replace(chr(10), ' ')}"
            )
    else:
        lines.append("- No new entries")
    lines.extend(
        [
            "",
            "Only participant and totals fields are compared. "
            "Local paths and extraction metadata are ignored.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path, help="Committed dataset")
    parser.add_argument("current", type=Path, help="Newly extracted dataset")
    parser.add_argument("--changed-file", type=Path, default=None)
    parser.add_argument("--previous-report", type=Path, default=None)
    parser.add_argument("--current-report", type=Path, default=None)
    args = parser.parse_args(argv)

    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    previous_report = (
        json.loads(args.previous_report.read_text(encoding="utf-8"))
        if args.previous_report is not None
        else None
    )
    current_report = (
        json.loads(args.current_report.read_text(encoding="utf-8"))
        if args.current_report is not None
        else None
    )
    result = compare(previous, current, previous_report, current_report)

    if args.changed_file is not None:
        args.changed_file.write_text(
            "true\n" if result["changed"] else "false\n", encoding="utf-8"
        )
    print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
