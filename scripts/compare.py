"""Compare two extracted CENIT datasets semantically."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXCLUDED_PARTICIPANT_FIELDS = {"posición"}


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


def compare(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    previous_records = participant_index(previous.get("participants", []))
    current_records = participant_index(current.get("participants", []))

    added = sorted(current_records.keys() - previous_records.keys())
    removed = sorted(previous_records.keys() - current_records.keys())
    changed = []
    for code in sorted(previous_records.keys() & current_records.keys()):
        changes = field_changes(previous_records[code], current_records[code])
        if changes:
            changed.append({"code": code, "fields": changes})

    totals_changes = field_changes(previous.get("totals", {}), current.get("totals", {}))

    return {
        "changed": bool(added or removed or changed or totals_changes),
        "added": added,
        "removed": removed,
        "changed_participants": changed,
        "totals_changes": totals_changes,
        "previous_participants": len(previous_records),
        "current_participants": len(current_records),
    }


def display(value: Any) -> str:
    if isinstance(value, str):
        return f"`{value}`" if value else "`(empty)`"
    if isinstance(value, bool):
        return "`true`" if value else "`false`"
    if value is None:
        return "`null`"
    return f"`{value}`"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# CENIT table diff",
        "",
        f"- Participants: {result['previous_participants']} -> {result['current_participants']}",
        f"- Added: {len(result['added'])}",
        f"- Removed: {len(result['removed'])}",
        f"- Changed: {len(result['changed_participants'])}",
        "",
        "Checksums, local paths and report metadata are ignored.",
        "",
    ]

    if result["added"]:
        lines.extend(["## Added participants", ""])
        lines.extend(f"- `{code}`" for code in result["added"])
        lines.append("")

    if result["removed"]:
        lines.extend(["## Removed participants", ""])
        lines.extend(f"- `{code}`" for code in result["removed"])
        lines.append("")

    if result["changed_participants"]:
        lines.extend(["## Changed participants", ""])
        for entry in result["changed_participants"]:
            lines.append(f"### `{entry['code']}`")
            lines.append("")
            for field in entry["fields"]:
                lines.append(
                    f"- `{field['path']}`: {display(field['before'])} -> "
                    f"{display(field['after'])}"
                )
            lines.append("")

    lines.extend(["## Totals", ""])
    if result["totals_changes"]:
        for field in result["totals_changes"]:
            lines.append(
                f"- `{field['path']}`: {display(field['before'])} -> "
                f"{display(field['after'])}"
            )
    else:
        lines.append("- No changes")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path, help="Committed dataset")
    parser.add_argument("current", type=Path, help="Newly extracted dataset")
    parser.add_argument("--changed-file", type=Path, default=None)
    args = parser.parse_args(argv)

    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    result = compare(previous, current)

    if args.changed_file is not None:
        args.changed_file.write_text(
            "true\n" if result["changed"] else "false\n", encoding="utf-8"
        )
    print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
