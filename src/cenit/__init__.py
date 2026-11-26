"""Document-specific extractor for the CENIT participants table.

The table lives on page 1 of the Banrep CENIT codes PDF. It has 15 physical
columns, 51 data rows (50 participants plus the totals row) and a header
whose labels are rotated 90 degrees clockwise.

The expected layout is a validation contract, not a placement rule. Column
boundaries are discovered from the PDF geometry, labels are reconstructed from
positioned glyphs, and data is emitted only when the contract checks pass.

Outputs use English envelope fields and Spanish domain keys:

    <output>.json             participants and totals
    <output>_report.json      structured extraction report
    <output>_debug.json       geometry, labels and the raw 51x15 matrix
    <output>.csv              flat 15-column view for manual review

Usage:

    uv run cenit --page 1 ../cenit_codes.pdf
    uv run cenit ../cenit_codes.pdf --output build/cenit
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pdfplumber


SCHEMA_VERSION = 2

EXPECTED_PARTICIPANTS = 50
EXPECTED_DATA_ROWS = EXPECTED_PARTICIPANTS + 1
EXPECTED_PHYSICAL_COLUMNS = 15
EXPECTED_BOUNDARIES = EXPECTED_PHYSICAL_COLUMNS + 1

TOTALS_ROW_LABEL = "TOTAL PARTICIPANTES EN CENIT"
TOTALS_ROW_TOKENS = tuple(TOTALS_ROW_LABEL.lower().split())

ENTITY_COLUMNS = {
    3: "bancos",
    4: "cooperativa_financiera",
    5: "corporación_financiera",
    6: "compañía_de_financiamiento",
    7: "entidad_del_estado",
    8: "operador_de_información",
    9: "seped",
}

EXPECTED_ENTITY_TOTALS = {
    "bancos": 27,
    "cooperativa_financiera": 4,
    "corporación_financiera": 1,
    "compañía_de_financiamiento": 8,
    "entidad_del_estado": 4,
    "operador_de_información": 23,
    "seped": 1,
}


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    index: int
    role: str
    parent: str | None
    rotated: bool


@dataclass(frozen=True)
class HeaderSpec:
    key: str
    label: str
    start: int
    end: int
    rotated: bool
    single_column: bool


COLUMNS = (
    ColumnSpec("participante", "Participante", 0, "column", None, False),
    ColumnSpec("código_cenit", "Código de Compensación CENIT", 1, "column", None, True),
    ColumnSpec("inicio_de_operación", "Inicio de Operación", 2, "column", None, True),
    ColumnSpec("bancos", "Bancos", 3, "subcolumn", "tipo_de_entidad", True),
    ColumnSpec(
        "cooperativa_financiera",
        "Cooperativa Financiera",
        4,
        "subcolumn",
        "tipo_de_entidad",
        True,
    ),
    ColumnSpec(
        "corporación_financiera",
        "Corporación Financiera",
        5,
        "subcolumn",
        "tipo_de_entidad",
        True,
    ),
    ColumnSpec(
        "compañía_de_financiamiento",
        "Compañía de Financiamiento",
        6,
        "subcolumn",
        "tipo_de_entidad",
        True,
    ),
    ColumnSpec(
        "entidad_del_estado", "Entidad del Estado", 7, "subcolumn", "tipo_de_entidad", True
    ),
    ColumnSpec(
        "operador_de_información",
        "Operador de Información",
        8,
        "subcolumn",
        "tipo_de_entidad",
        True,
    ),
    ColumnSpec("seped", "SEPED", 9, "subcolumn", "tipo_de_entidad", True),
    ColumnSpec(
        "aplica_transacciones_débito",
        "Aplica Transacciones Débito",
        10,
        "column",
        None,
        True,
    ),
    ColumnSpec(
        "cuenta_de_ahorros",
        "Cuenta de Ahorros",
        11,
        "subcolumn",
        "tipo_de_cuenta_y_longitud",
        True,
    ),
    ColumnSpec(
        "cuenta_corriente",
        "Cuenta Corriente",
        12,
        "subcolumn",
        "tipo_de_cuenta_y_longitud",
        True,
    ),
    ColumnSpec(
        "depósito_electrónico_o_de_bajo_monto_longitud",
        "Depósito Electrónico o de Bajo Monto",
        13,
        "subcolumn",
        "depósito_electrónico_o_de_bajo_monto",
        True,
    ),
    ColumnSpec(
        "depósito_electrónico_o_de_bajo_monto_nombre",
        "Depósito Electrónico o de Bajo Monto",
        14,
        "subcolumn",
        "depósito_electrónico_o_de_bajo_monto",
        True,
    ),
)

HEADERS = (
    HeaderSpec("participante", "Participante", 0, 1, False, True),
    HeaderSpec("código_cenit", "Código de Compensación CENIT", 1, 2, True, True),
    HeaderSpec("inicio_de_operación", "Inicio de Operación", 2, 3, True, True),
    HeaderSpec("bancos", "Bancos", 3, 4, True, True),
    HeaderSpec("cooperativa_financiera", "Cooperativa Financiera", 4, 5, True, True),
    HeaderSpec("corporación_financiera", "Corporación Financiera", 5, 6, True, True),
    HeaderSpec(
        "compañía_de_financiamiento", "Compañía de Financiamiento", 6, 7, True, True
    ),
    HeaderSpec("entidad_del_estado", "Entidad del Estado", 7, 8, True, True),
    HeaderSpec("operador_de_información", "Operador de Información", 8, 9, True, True),
    HeaderSpec("seped", "SEPED", 9, 10, True, True),
    HeaderSpec(
        "aplica_transacciones_débito", "Aplica Transacciones Débito", 10, 11, True, True
    ),
    HeaderSpec("cuenta_de_ahorros", "Cuenta de Ahorros", 11, 12, True, True),
    HeaderSpec("cuenta_corriente", "Cuenta Corriente", 12, 13, True, True),
    HeaderSpec("tipo_de_entidad", "Tipo de Entidad", 3, 10, False, False),
    HeaderSpec("tipo_de_cuenta_y_longitud", "Tipo de Cuenta y Longitud", 11, 15, False, False),
    HeaderSpec(
        "depósito_electrónico_o_de_bajo_monto",
        "Depósito Electrónico o de Bajo Monto",
        13,
        15,
        True,
        False,
    ),
)

BOUNDARY_OFFSET = 0.8
ROTATED_MATRIX_TOLERANCE = 0.1


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).replace("\u00a0", " ")).strip()


def normalize_label(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]", "", value.lower())


def is_totals_label(value: str) -> bool:
    tokens = tuple(token.lower() for token in clean_text(value).split())
    return tokens == TOTALS_ROW_TOKENS


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def group_positions(values: list[float], tolerance: float) -> list[float]:
    values = sorted(values)
    if not values:
        return []
    groups = [[values[0]]]
    for value in values[1:]:
        if value - groups[-1][-1] <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [statistics.median(group) for group in groups]


def union_length(intervals: list[tuple[float, float]]) -> float:
    if not intervals:
        return 0.0
    ordered = sorted(intervals)
    start, end = ordered[0]
    total = 0.0
    for left, right in ordered[1:]:
        if left <= end:
            end = max(end, right)
        else:
            total += end - start
            start, end = left, right
    return total + end - start


def find_grid(page: Any) -> tuple[list[float], list[float], list[float]]:
    """Return x boundaries, y boundaries and the raw data row boundaries."""
    tall_curves = [
        curve
        for curve in page.curves
        if curve["width"] < 2 and curve["height"] > page.height * 0.5
    ]
    if not tall_curves:
        raise ValueError("No tall vertical dividers were found on the page.")

    x_boundaries = group_positions(
        [float(curve["x0"]) for curve in tall_curves], tolerance=1.0
    )
    if len(x_boundaries) != EXPECTED_BOUNDARIES:
        raise ValueError(
            f"Expected {EXPECTED_BOUNDARIES} vertical boundaries, "
            f"found {len(x_boundaries)}: {[round(x, 2) for x in x_boundaries]}"
        )

    left, right = x_boundaries[0], x_boundaries[-1]
    data_top = min(float(curve["top"]) for curve in tall_curves)
    data_bottom = max(float(curve["bottom"]) for curve in tall_curves)

    segments: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for edge in page.edges:
        if edge.get("orientation") != "h":
            continue
        y = float(edge["top"])
        start = max(float(edge["x0"]), left)
        end = min(float(edge["x1"]), right)
        if data_top - 5 <= y <= page.height and end > start:
            segments[round(y, 1)].append((start, end))

    y_candidates = [
        y
        for y, spans in segments.items()
        if union_length(spans) >= (right - left) * 0.9
    ]
    y_boundaries = group_positions(y_candidates, tolerance=1.2)
    if len(y_boundaries) < EXPECTED_BOUNDARIES:
        raise ValueError(
            f"Expected at least {EXPECTED_BOUNDARIES} horizontal boundaries, "
            f"found {len(y_boundaries)}."
        )

    return x_boundaries, y_boundaries, [data_top, data_bottom]


def find_data_boundaries(page: Any, x_boundaries: list[float], y_boundaries: list[float]) -> list[float]:
    """Cut the horizontal boundaries at the bottom of the totals row."""
    words = page.extract_words()
    total_words = [
        word
        for word in words
        if normalize_label(word["text"]) == "total"
        and x_boundaries[0] <= word["x0"] <= x_boundaries[-1]
    ]
    if len(total_words) != 1:
        raise ValueError(
            f"Expected one totals-row label, found {len(total_words)}."
        )

    center_y = (total_words[0]["top"] + total_words[0]["bottom"]) / 2
    for index in range(len(y_boundaries) - 1):
        if y_boundaries[index] <= center_y < y_boundaries[index + 1]:
            boundaries = y_boundaries[: index + 2]
            expected = EXPECTED_DATA_ROWS + 1
            if len(boundaries) != expected:
                raise ValueError(
                    f"Expected {expected} data-row boundaries, "
                    f"found {len(boundaries)}."
                )
            return boundaries
    raise ValueError("The totals-row label is outside the detected row grid.")


def column_index_for_x(x: float, x_boundaries: list[float]) -> int | None:
    shifted = x + BOUNDARY_OFFSET
    for index in range(len(x_boundaries) - 1):
        if x_boundaries[index] <= shifted < x_boundaries[index + 1]:
            return index
    return None


def is_rotated(char: dict[str, Any]) -> bool:
    return abs(float(char["matrix"][0])) < ROTATED_MATRIX_TOLERANCE


def read_header_text(
    page: Any, x_boundaries: list[float], header_bottom: float, spec: HeaderSpec
) -> str:
    chars = [
        char
        for char in page.chars
        if 120 <= char["top"] < header_bottom and char["text"].strip()
    ]
    chars = [char for char in chars if is_rotated(char) == spec.rotated]
    if spec.single_column:
        chars = [
            char
            for char in chars
            if column_index_for_x(char["x0"], x_boundaries) == spec.start
        ]
    else:
        left = x_boundaries[spec.start] + BOUNDARY_OFFSET
        right = x_boundaries[spec.end] + BOUNDARY_OFFSET
        chars = [char for char in chars if left <= char["x0"] < right]

    groups: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for char in chars:
        key = round(char["x0"], 1) if spec.rotated else round(char["top"], 1)
        groups[key].append(char)

    lines = []
    for key in sorted(groups, reverse=spec.rotated):
        order_key = "top" if spec.rotated else "x0"
        lines.append("".join(char["text"] for char in sorted(groups[key], key=lambda c: c[order_key])))
    return " ".join(lines)


def validate_headers(
    page: Any, x_boundaries: list[float], header_bottom: float
) -> list[dict[str, Any]]:
    results = []
    for spec in HEADERS:
        found = read_header_text(page, x_boundaries, header_bottom, spec)
        matches = normalize_label(found) == normalize_label(spec.label)
        results.append(
            {
                "key": spec.key,
                "label": spec.label,
                "role": "parent" if not spec.single_column else "label",
                "physical_columns": [spec.start + 1, spec.end],
                "rotated": spec.rotated,
                "expected": spec.label,
                "found": found,
                "matched": matches,
            }
        )
    return results


def extract_matrix(page: Any, x_boundaries: list[float], y_boundaries: list[float]) -> list[list[str]]:
    words = page.extract_words()
    cells: dict[tuple[int, int], dict[float, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for word in words:
        center_x = (word["x0"] + word["x1"]) / 2
        center_y = (word["top"] + word["bottom"]) / 2
        col = column_index_for_x(center_x, x_boundaries)
        if col is None:
            continue
        for row in range(len(y_boundaries) - 1):
            if y_boundaries[row] <= center_y < y_boundaries[row + 1]:
                cells[(row, col)][round(word["top"], 1)].append(word)
                break

    matrix = []
    for row in range(len(y_boundaries) - 1):
        values = []
        for col in range(len(x_boundaries) - 1):
            lines = []
            for top in sorted(cells[(row, col)]):
                line_words = sorted(cells[(row, col)][top], key=lambda w: w["x0"])
                lines.append(" ".join(word["text"] for word in line_words))
            values.append(" ".join(lines))
        matrix.append(values)
    return matrix


def issue(code: str, message: str, **location: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"code": code, "message": message}
    if location:
        entry["location"] = location
    return entry


def convert_participant(row: list[str], position: int) -> dict[str, Any]:
    tipo_de_entidad = {}
    for index, key in ENTITY_COLUMNS.items():
        mark = clean_text(row[index]).upper()
        if mark not in ("", "X"):
            raise ValueError(
                f"Unexpected entity mark {mark!r} in column {index + 1}, row {position}."
            )
        tipo_de_entidad[key] = mark == "X"

    applies = normalize_label(row[10])
    return {
        "posición": position,
        "participante": clean_text(row[0]),
        "código_cenit": clean_text(row[1]),
        "inicio_de_operación": clean_text(row[2]),
        "tipo_de_entidad": tipo_de_entidad,
        "aplica_transacciones_débito": (
            "SI" if applies == "si" else "NO" if applies == "no" else clean_text(row[10])
        ),
        "tipo_de_cuenta_y_longitud": {
            "cuenta_de_ahorros": clean_text(row[11]),
            "cuenta_corriente": clean_text(row[12]),
            "depósito_electrónico_o_de_bajo_monto": {
                "longitud": clean_text(row[13]),
                "nombre": clean_text(row[14]),
            },
        },
    }


def validate_records(
    records: list[dict[str, Any]], total_row: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    unextracted: list[dict[str, Any]] = []

    codes = [record["código_cenit"] for record in records]
    duplicates = sorted({code for code in codes if codes.count(code) > 1})
    if duplicates:
        issues.append(issue("duplicate_codes", "Duplicate CENIT codes found.", codes=duplicates))

    if len(records) != EXPECTED_PARTICIPANTS:
        issues.append(
            issue(
                "participant_count",
                f"Expected {EXPECTED_PARTICIPANTS} participants, found {len(records)}.",
            )
        )

    required = {
        "participante": "participante",
        "código_cenit": "código_cenit",
        "inicio_de_operación": "inicio_de_operación",
        "aplica_transacciones_débito": "aplica_transacciones_débito",
    }
    for record in records:
        position = record["posición"]
        for key, column in required.items():
            if not record[key]:
                unextracted.append(
                    {
                        "row": position,
                        "column": column,
                        "reason": "empty_cell",
                    }
                )

        if not re.fullmatch(r"\d{3,5}", record["código_cenit"]):
            issues.append(
                issue(
                    "invalid_cenit_code",
                    f"Invalid CENIT code {record['código_cenit']!r}.",
                    row=position,
                    column="código_cenit",
                )
            )
        if not re.fullmatch(r"\(\*\)|\d{1,2}/\d{1,2}/\d{4}", record["inicio_de_operación"]):
            issues.append(
                issue(
                    "unexpected_operation_start",
                    f"Unexpected operation start {record['inicio_de_operación']!r}.",
                    row=position,
                    column="inicio_de_operación",
                )
            )
        if normalize_label(record["aplica_transacciones_débito"]) not in ("si", "no"):
            issues.append(
                issue(
                    "unexpected_debit_flag",
                    f"Unexpected debit flag {record['aplica_transacciones_débito']!r}.",
                    row=position,
                    column="aplica_transacciones_débito",
                )
            )

    for key, expected in EXPECTED_ENTITY_TOTALS.items():
        obtained = sum(record["tipo_de_entidad"][key] for record in records)
        if obtained != expected:
            issues.append(
                issue(
                    "entity_total_mismatch",
                    f"Expected {expected} rows for {key}, counted {obtained}.",
                    column=key,
                    expected=expected,
                    found=obtained,
                )
            )

    if not is_totals_label(total_row[0] if total_row else ""):
        issues.append(
            issue(
                "totals_label",
                f"The totals row does not contain {TOTALS_ROW_LABEL!r}.",
                row=EXPECTED_DATA_ROWS,
            )
        )
    if clean_text(total_row[1] if len(total_row) > 1 else "") != str(EXPECTED_PARTICIPANTS):
        issues.append(
            issue(
                "totals_participants",
                f"The totals row should contain {EXPECTED_PARTICIPANTS} participants.",
                row=EXPECTED_DATA_ROWS,
                column="código_cenit",
            )
        )
    for index, key in ENTITY_COLUMNS.items():
        expected = str(EXPECTED_ENTITY_TOTALS[key])
        found = clean_text(total_row[index] if len(total_row) > index else "")
        if found != expected:
            issues.append(
                issue(
                    "totals_entity_mismatch",
                    f"Totals row column {index + 1}: expected {expected}, found {found!r}.",
                    row=EXPECTED_DATA_ROWS,
                    column=key,
                    expected=expected,
                    found=found,
                )
            )

    return issues, unextracted


def build_column_report(
    x_boundaries: list[float], matrix: list[list[str]], headers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    header_by_key = {header["key"]: header for header in headers}
    parent_keys = {spec.parent for spec in COLUMNS if spec.parent}
    parent_headers = {
        key: header_by_key[key] for key in parent_keys if key in header_by_key
    }

    report = []
    for spec in COLUMNS:
        left = x_boundaries[spec.index]
        right = x_boundaries[spec.index + 1]
        parent = parent_headers.get(spec.parent or "")
        header = header_by_key.get(spec.key, parent)
        if header is None:
            raise KeyError(spec.key)
        values = [row[spec.index] for row in matrix[:-1]]
        report.append(
            {
                "key": spec.key,
                "label": spec.label,
                "role": spec.role,
                "parent": spec.parent,
                "physical_index": spec.index,
                "x_range": [round(left, 2), round(right, 2)],
                "expected_label": header["expected"],
                "label_found": header["found"],
                "label_matched": header["matched"],
                "parent_label_matched": parent["matched"] if parent else None,
                "kept": header["matched"] and (parent is None or parent["matched"]),
                "ignored": not (header["matched"] and (parent is None or parent["matched"])),
                "rows_with_value": sum(bool(value) for value in values),
                "rows_empty": len(values) - sum(bool(value) for value in values),
            }
        )
    return report


def build_report(
    result: dict[str, Any], headers: list[dict[str, Any]], issues: list[dict[str, Any]],
    unextracted: list[dict[str, Any]],
) -> dict[str, Any]:
    columns = result["column_report"]
    failed_labels = [header for header in headers if not header["matched"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "source": result["source"],
        "status": "ok" if not issues and not unextracted and not failed_labels else "review",
        "grid": {
            "x_boundaries": result["x_boundaries"],
            "y_boundaries": result["y_boundaries"],
            "data_y_range": result["data_y_range"],
        },
        "summary": {
            "expected_physical_columns": EXPECTED_PHYSICAL_COLUMNS,
            "found_physical_columns": len(result["x_boundaries"]) - 1,
            "physical_columns_kept": sum(1 for column in columns if column["kept"]),
            "physical_columns_ignored": sum(1 for column in columns if column["ignored"]),
            "expected_labels": len(HEADERS),
            "labels_found": len(headers) - len(failed_labels),
            "labels_ignored": len(failed_labels),
            "entity_subcolumns": len(ENTITY_COLUMNS),
            "account_subcolumns": 4,
            "expected_data_rows": EXPECTED_DATA_ROWS,
            "found_data_rows": result["row_count"],
            "participant_rows_used": len(result["records"]),
            "totals_rows_used": 1,
            "unextracted_cells": len(unextracted),
        },
        "headers": headers,
        "columns": columns,
        "unextracted": unextracted,
        "issues": issues,
    }


def write_outputs(result: dict[str, Any], report: dict[str, Any], prefix: Path, allow_errors: bool) -> dict[str, Path]:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}

    data_path = prefix.with_suffix(".json")
    debug_path = prefix.with_name(prefix.name + "_debug.json")
    report_path = prefix.with_name(prefix.name + "_report.json")
    csv_path = prefix.with_suffix(".csv")

    data = {
        "schema_version": SCHEMA_VERSION,
        "source": result["source"],
        "participants": result["records"],
        "totals": result["totals"],
    }

    debug = {
        "schema_version": SCHEMA_VERSION,
        "source": result["source"],
        "grid": report["grid"],
        "headers": report["headers"],
        "raw_matrix": result["matrix"],
    }

    if report["status"] == "ok" or allow_errors:
        data_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        outputs["data"] = data_path

    debug_path.write_text(
        json.dumps(debug, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    outputs["debug"] = debug_path
    outputs["report"] = report_path

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([column.key for column in COLUMNS])
        writer.writerows(result["matrix"])
    outputs["csv"] = csv_path

    return outputs


def extract(pdf_path: Path, page_number: int, source_url: str | None) -> dict[str, Any]:
    with pdfplumber.open(pdf_path) as pdf:
        if not 1 <= page_number <= len(pdf.pages):
            raise ValueError(
                f"Page {page_number} does not exist; the PDF has {len(pdf.pages)} pages."
            )
        page = pdf.pages[page_number - 1]

        x_boundaries, y_boundaries, data_y_range = find_grid(page)
        y_boundaries = find_data_boundaries(page, x_boundaries, y_boundaries)
        header_bottom = data_y_range[0]
        matrix = extract_matrix(page, x_boundaries, y_boundaries)
        headers = validate_headers(page, x_boundaries, header_bottom)

    if len(matrix) != EXPECTED_DATA_ROWS or any(
        len(row) != EXPECTED_PHYSICAL_COLUMNS for row in matrix
    ):
        raise ValueError(
            f"Expected a {EXPECTED_DATA_ROWS}x{EXPECTED_PHYSICAL_COLUMNS} matrix, "
            f"got {len(matrix)} rows."
        )

    records = [
        convert_participant(row, position)
        for position, row in enumerate(matrix[:-1], start=1)
    ]

    total_row = matrix[-1]
    issues, unextracted = validate_records(records, total_row)
    for header in headers:
        if not header["matched"]:
            issues.append(
                issue(
                    "header_mismatch",
                    f"Header {header['key']!r} did not match its expected label.",
                    expected=header["expected"],
                    found=header["found"],
                    physical_columns=header["physical_columns"],
                )
            )

    result = {
        "source": {
            "file": str(pdf_path),
            "sha256": file_sha256(pdf_path),
            "page": page_number,
            "url": source_url,
        },
        "x_boundaries": [round(value, 2) for value in x_boundaries],
        "y_boundaries": [round(value, 2) for value in y_boundaries],
        "data_y_range": [round(value, 2) for value in data_y_range],
        "row_count": len(matrix),
        "matrix": matrix,
        "records": records,
        "totals": {
            "participantes": clean_text(total_row[1]),
            "tipo_de_entidad": {
                key: clean_text(total_row[index]) for index, key in ENTITY_COLUMNS.items()
            },
        },
    }
    result["column_report"] = build_column_report(x_boundaries, matrix, headers)
    result["headers"] = headers
    result["issues"] = issues
    result["unextracted"] = unextracted
    result["report"] = build_report(result, headers, issues, unextracted)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract the CENIT participants table from the Banrep PDF."
    )
    parser.add_argument("pdf", type=Path, help="Path to the source PDF")
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page containing the table, numbered from 1 (default: 1)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cenit"),
        help="Prefix for output files, without extension",
    )
    parser.add_argument(
        "--source-url",
        default=None,
        help="Source URL recorded in the report",
    )
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help="Write the data file even when validation reports problems",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.pdf.is_file():
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    try:
        result = extract(args.pdf, args.page, args.source_url)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    report = result["report"]
    outputs = write_outputs(result, report, args.output, args.allow_errors)

    print(f"Status:    {report['status']}")
    print(f"Rows:      {report['summary']['participant_rows_used']} participants + 1 totals row")
    print(f"Columns:   {report['summary']['physical_columns_kept']}/15 kept")
    print(f"Labels:    {report['summary']['labels_found']}/{report['summary']['expected_labels']} matched")
    for name, path in outputs.items():
        print(f"{name.title():<10} {path}")

    if report["status"] == "review":
        for entry in report["issues"]:
            print(f" - {entry['code']}: {entry['message']}", file=sys.stderr)
        for entry in report["unextracted"]:
            print(
                f" - empty {entry['column']} at row {entry['row']}", file=sys.stderr
            )
        if not args.allow_errors:
            print("Data file omitted; inspect the report and debug files.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
