"""Rich rendering helpers and the Textual explorer for CENIT values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Literal

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from ._types import (
    ENTITY_TYPES,
    AccountCapabilities,
    AccountNumberLengthScope,
    AccountNumberLengthVariant,
    AccountType,
    EntityTypeTotals,
    ParticipantRecord,
    Totals,
)

Language = Literal["en", "es", "eng", "spa"]

LANGUAGE_ALIASES = {"en": "en", "eng": "en", "es": "es", "spa": "es"}

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "row_number": "Row",
        "participant_name": "Participant",
        "cenit_code": "CENIT Compensation Code",
        "operation_start_date": "Operation Start",
        "operation_start_note": "Operation Start Note",
        "entity_types": "Entity Type",
        "supports_debit_transactions": "Applies Debit Transactions",
        "account_capabilities": "Account Type and Length",
        "electronic_or_low_value_deposit_name": "Electronic or Low Value Deposit Name",
        "footnotes": "Footnotes",
        "participants": "Participants",
        "bank": "Banks",
        "financial_cooperative": "Financial Cooperative",
        "financial_corporation": "Financial Corporation",
        "financing_company": "Financing Company",
        "government_entity": "Government Entity",
        "information_operator": "Information Operator",
        "sedpe": "SEDPE",
        "savings_account_number_lengths": "Savings Account",
        "checking_account_number_lengths": "Checking Account",
        "electronic_or_low_value_deposit_number_lengths": "Electronic or Low Value Deposit",
        "lengths": "Lengths",
        "footnote_markers": "Markers",
        "scope": "Scope",
        "account_type": "Account Type",
        "field": "Field",
        "value": "Value",
        "values": "Values",
        "mapping": "Mapping",
    },
    "es": {
        "row_number": "Fila",
        "participant_name": "Participante",
        "cenit_code": "Código de Compensación CENIT",
        "operation_start_date": "Inicio de Operación",
        "operation_start_note": "Nota de Inicio de Operación",
        "entity_types": "Tipo de Entidad",
        "supports_debit_transactions": "Aplica Transacciones Débito",
        "account_capabilities": "Tipo de Cuenta y Longitud",
        "electronic_or_low_value_deposit_name": "Nombre del Depósito Electrónico o de Bajo Monto",
        "footnotes": "Notas",
        "participants": "Participantes",
        "bank": "Bancos",
        "financial_cooperative": "Cooperativa Financiera",
        "financial_corporation": "Corporación Financiera",
        "financing_company": "Compañía de Financiamiento",
        "government_entity": "Entidad del Estado",
        "information_operator": "Operador de Información",
        "sedpe": "SEDPE",
        "savings_account_number_lengths": "Cuenta de Ahorros",
        "checking_account_number_lengths": "Cuenta Corriente",
        "electronic_or_low_value_deposit_number_lengths": "Depósito Electrónico o de Bajo Monto",
        "lengths": "Longitudes",
        "footnote_markers": "Marcadores",
        "scope": "Alcance",
        "account_type": "Tipo de Cuenta",
        "field": "Campo",
        "value": "Valor",
        "values": "Valores",
        "mapping": "Mapa",
    },
}

FOOTNOTE_DEFINITIONS: dict[str, dict[str, str]] = {
    "en": {
        "(*)": "Linked before May 2025",
        "(**)": "Used for special collection agreements",
        "(***)": "Includes leading zeros",
        "(****)": "Electronic deposit service available but not enabled in CENIT",
    },
    "es": {
        "(*)": "Vinculación antes de mayo de 2025",
        "(**)": "Utilizadas para convenios especiales de recaudo",
        "(***)": "Incluye ceros iniciales",
        "(****)": "La entidad cuenta con el servicio de Depósitos Electrónicos pero no estará habilitado en CENIT",
    },
}

SCOPE_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "standard": "standard",
        "special_collection_agreement": "special collection agreement",
        "includes_leading_zeros": "includes leading zeros",
        "electronic_deposit_not_enabled_in_cenit": "not enabled in CENIT",
        "linked_before_may_2025": "linked before May 2025",
    },
    "es": {
        "standard": "estándar",
        "special_collection_agreement": "convenio especial de recaudo",
        "includes_leading_zeros": "incluye ceros iniciales",
        "electronic_deposit_not_enabled_in_cenit": "no habilitado en CENIT",
        "linked_before_may_2025": "vinculado antes de mayo de 2025",
    },
}

ENTITY_TYPE_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "bank": "Bank",
        "financial_cooperative": "Financial Cooperative",
        "financial_corporation": "Financial Corporation",
        "financing_company": "Financing Company",
        "government_entity": "Government Entity",
        "information_operator": "Information Operator",
        "sedpe": "SEDPE",
    },
    "es": {
        "bank": "Banco",
        "financial_cooperative": "Cooperativa Financiera",
        "financial_corporation": "Corporación Financiera",
        "financing_company": "Compañía de Financiamiento",
        "government_entity": "Entidad del Estado",
        "information_operator": "Operador de Información",
        "sedpe": "SEDPE",
    },
}

ACCOUNT_TYPE_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "savings": "savings",
        "checking": "checking",
        "electronic_or_low_value_deposit": "electronic or low value deposit",
    },
    "es": {
        "savings": "ahorros",
        "checking": "corriente",
        "electronic_or_low_value_deposit": "depósito electrónico o de bajo valor",
    },
}

COLUMN_STYLES: dict[str, str] = {
    "participant_name": "bold bright_white",
    "cenit_code": "bright_cyan",
    "operation_start_date": "bright_green",
    "operation_start_note": "bright_yellow",
    "footnotes": "bright_magenta",
    "scope": "bright_magenta",
    "row_number": "bright_white",
    "participants": "bold bright_cyan",
}

DEFAULT_COLUMNS: dict[type, tuple[str, ...]] = {
    ParticipantRecord: (
        "row_number",
        "participant_name",
        "cenit_code",
        "operation_start_date",
        "entity_types",
        "supports_debit_transactions",
        "savings_account_number_lengths",
        "checking_account_number_lengths",
        "electronic_or_low_value_deposit_number_lengths",
        "electronic_or_low_value_deposit_name",
    ),
    Totals: ("participants", *ENTITY_TYPES),
    EntityTypeTotals: ENTITY_TYPES,
    AccountCapabilities: (
        "savings_account_number_lengths",
        "checking_account_number_lengths",
        "electronic_or_low_value_deposit_number_lengths",
    ),
    AccountNumberLengthVariant: ("lengths", "footnote_markers", "scope"),
}

EXPORT_FORMATS = {".txt": "text", ".html": "html", ".svg": "svg"}


@dataclass(frozen=True)
class _TableSection:
    title: str
    columns: tuple[tuple[str, str], ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class View:
    """Configuration for rendering CENIT values as tables."""

    language: Language = "en"
    columns: tuple[str, ...] | None = None
    exclude: tuple[str, ...] = ()
    show_columns: bool = True
    keep_excluded_columns: bool = False
    title: str | None = None
    separator: bool = True
    separator_style: str = "dim"
    show_footnotes: bool = True
    row_columns: Mapping[int, tuple[str, ...]] = field(default_factory=dict)
    width: int | None = None

    def __post_init__(self) -> None:
        try:
            normalized = LANGUAGE_ALIASES[self.language.lower()]
        except (AttributeError, KeyError) as exc:
            raise ValueError(f"unsupported language: {self.language}") from exc
        object.__setattr__(self, "language", normalized)

    def render(self, value: Any) -> RenderableType:
        """Return a Rich renderable for ``value``."""
        sections = self.sections(value)
        footnotes = self.footnote_items(value) if self.show_footnotes else ()
        if not sections and not footnotes:
            return Group()
        renderables: list[RenderableType] = []
        for index, section in enumerate(sections):
            if index and self.separator:
                renderables.append(Rule(style=self.separator_style))
            renderables.append(self._rich_table(section))
        if footnotes:
            if renderables and self.separator:
                renderables.append(Rule(style=self.separator_style))
            renderables.append(self._footnote_block(footnotes))
        if len(renderables) == 1:
            return renderables[0]
        result: RenderableType = Group(*renderables)
        if self.title:
            return Group(Rule(self.title, style=self.separator_style), result)
        return result

    def sections(self, value: Any) -> tuple[_TableSection, ...]:
        """Return normalized table sections for ``value``."""
        if is_dataclass(value) and not isinstance(value, type):
            return (self._records_section([value], type(value)),)
        if isinstance(value, Mapping):
            return (self._mappings_section([value]),)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            items = list(value)
            if not items:
                return ()
            if all(
                isinstance(item, Sequence) and not isinstance(item, (str, bytes))
                for item in items
            ):
                return (self._matrix_section(items),)
            sections: list[_TableSection] = []
            for kind, group_items, cls in self._group_items(items):
                if kind == "nested":
                    sections.extend(self.sections(group_items[0]))
                elif kind == "records":
                    sections.append(self._records_section(group_items, cls or type(group_items[0])))
                elif kind == "mappings":
                    sections.append(self._mappings_section(group_items))
                else:
                    sections.append(self._scalar_section(group_items))
            return tuple(sections)
        if isinstance(value, Enum):
            return (self._enum_section(value),)
        return (self._scalar_section([value]),)

    def display(self, value: Any, *, console: Console | None = None) -> None:
        """Print ``value`` to a Rich console."""
        (console or Console(width=self.width)).print(self.render(value))

    def explore(self, value: Any) -> None:
        """Open ``value`` in the Textual table explorer."""
        from ._tui import run_explorer

        run_explorer(self, value)

    def footnote_items(self, value: Any) -> tuple[tuple[str, str], ...]:
        """Return marker and definition pairs found in ``value``."""
        definitions = FOOTNOTE_DEFINITIONS[self.language]
        markers = sorted(
            self._collect_markers(value, []),
            key=lambda marker: (len(marker), marker),
        )
        return tuple((marker, definitions[marker]) for marker in markers if marker in definitions)

    def to_text(self, value: Any) -> str:
        """Render ``value`` to plain text."""
        return self._export(value, "text")

    def to_html(self, value: Any) -> str:
        """Render ``value`` to standalone HTML."""
        return self._export(value, "html")

    def to_svg(self, value: Any) -> str:
        """Render ``value`` to SVG."""
        return self._export(value, "svg")

    def save(self, value: Any, path: str | Path, *, format: str | None = None) -> Path:
        """Render ``value`` and write it to ``path``."""
        target = Path(path)
        export_format = format or EXPORT_FORMATS.get(target.suffix.lower(), "text")
        content = self._export(value, export_format)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def _collect_markers(self, value: Any, found: list[str]) -> list[str]:
        if is_dataclass(value) and not isinstance(value, type):
            note = getattr(value, "operation_start_note", None)
            if note:
                self._collect_markers(note, found)
            footnotes = getattr(value, "footnotes", ())
            if isinstance(footnotes, (tuple, list, set, frozenset)):
                for marker in footnotes:
                    self._collect_markers(marker, found)
            for item in fields(value):
                self._collect_markers(getattr(value, item.name), found)
        elif isinstance(value, Mapping):
            for item in value.values():
                self._collect_markers(item, found)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for item in value:
                self._collect_markers(item, found)
        elif isinstance(value, str) and value.startswith("(") and value.endswith(")"):
            if value not in found:
                found.append(value)
        return found

    def _footnote_block(self, items: tuple[tuple[str, str], ...]) -> Panel:
        table = Table.grid(padding=(0, 1))
        for marker, definition in items:
            table.add_row(Text(marker, style="bright_magenta"), definition)
        return Panel(table, title=self._label("footnotes"), border_style="bright_black")

    def _export(self, value: Any, format: str) -> str:
        console = Console(record=True, width=self.width, file=StringIO())
        console.print(self.render(value))
        if format == "text":
            return console.export_text()
        if format == "html":
            return console.export_html(inline_styles=True)
        if format == "svg":
            return console.export_svg(title=self.title or "cenit")
        raise ValueError(f"unsupported export format: {format}")

    def _label(self, name: str) -> str:
        return LABELS[self.language].get(name, name.replace("_", " ").title())

    def _format_record_value(self, record: Mapping[str, Any], name: str) -> str:
        value = record.get(name)
        if name == "operation_start_date" and value is None:
            return self._format(record.get("operation_start_note"))
        return self._format(value)

    def _format(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, bool):
            return {"en": ("no", "yes"), "es": ("no", "sí")}[self.language][int(bool(value))]
        if isinstance(value, AccountNumberLengthScope):
            return SCOPE_LABELS[self.language].get(value.value, value.value)
        if isinstance(value, AccountType):
            return ACCOUNT_TYPE_LABELS[self.language].get(value.value, value.value)
        if isinstance(value, Enum):
            return str(value.value)
        if isinstance(value, AccountNumberLengthVariant):
            return self._format_variant(value)
        if isinstance(value, Mapping):
            return ", ".join(f"{key}: {self._format(item)}" for key, item in value.items())
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return ", ".join(self._format(item) for item in value)
        if is_dataclass(value) and not isinstance(value, type):
            data = self._flatten_record(value)
            return ", ".join(f"{key}={self._format(item)}" for key, item in data.items())
        if isinstance(value, str):
            return ENTITY_TYPE_LABELS[self.language].get(value, value)
        return str(value)

    def _format_variant(self, variant: AccountNumberLengthVariant) -> str:
        parts = [", ".join(str(length) for length in variant.lengths)]
        if variant.footnote_markers:
            parts.append(" ".join(variant.footnote_markers))
        if variant.scope is not AccountNumberLengthScope.STANDARD:
            parts.append(self._format(variant.scope))
        return " ".join(part for part in parts if part)

    def _flatten_record(self, value: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for item in fields(value):
            child = getattr(value, item.name)
            if is_dataclass(child) and not isinstance(child, type):
                for key, nested in self._flatten_record(child).items():
                    data[key if key not in data else f"{item.name}.{key}"] = nested
            else:
                data[item.name] = child
        return data

    def _columns(self, key: str) -> tuple[str, str]:
        return key, self._label(key)

    def _title_for(self, cls: type, count: int) -> str:
        if self.title and count == 1:
            return self.title
        name = cls.__name__
        return f"{name} ({count})" if count > 1 else name

    def _select(self, base: tuple[str, ...], available: tuple[str, ...], count: int) -> tuple[list[str], list[tuple[str, ...]]]:
        base = tuple(name for name in base if name in available)
        specs: list[tuple[str, ...]] = []
        for index in range(count):
            override = self.row_columns.get(index)
            selected = base if override is None else tuple(name for name in override if name in available)
            specs.append(tuple(name for name in selected if name not in self.exclude))
        columns: list[str] = []
        for spec in specs:
            for name in spec:
                if name not in columns:
                    columns.append(name)
        if self.keep_excluded_columns:
            for name in base:
                if name in self.exclude and name not in columns:
                    columns.append(name)
        return columns, specs

    def _records_section(self, items: Sequence[Any], cls: type) -> _TableSection:
        records = [self._flatten_record(item) for item in items]
        available = tuple(dict.fromkeys(name for record in records for name in record))
        base = self.columns or DEFAULT_COLUMNS.get(cls, available)
        column_names, specs = self._select(base, available, len(items))
        rows = tuple(
            tuple(
                self._format_record_value(record, name)
                if name in spec and name not in self.exclude
                else ""
                for name in column_names
            )
            for record, spec in zip(records, specs)
        )
        return _TableSection(
            self._title_for(cls, len(items)),
            tuple(self._columns(name) for name in column_names),
            rows,
        )

    def _mappings_section(self, items: Sequence[Mapping[Any, Any]]) -> _TableSection:
        keys = list(dict.fromkeys(key for item in items for key in item))
        if self.columns:
            keys = [key for key in keys if str(key) in self.columns]
        keys = [key for key in keys if str(key) not in self.exclude]
        rows = tuple(
            (self._label("value"),)
            + tuple(self._format(item.get(key)) if key in item else "" for key in keys)
            for item in items
        )
        columns = (self._columns("field"),) + tuple(self._columns(str(key)) for key in keys)
        return _TableSection(self.title or self._label("mapping"), columns, rows)

    def _matrix_section(self, rows: Sequence[Sequence[Any]]) -> _TableSection:
        width = max((len(row) for row in rows), default=0)
        keys = [str(index + 1) for index in range(width)]
        if self.columns:
            keys = [key for key in keys if key in self.columns]
        formatted = tuple(
            tuple(self._format(row[index]) if index < len(row) else "" for index in range(len(keys)))
            for row in rows
        )
        return _TableSection(
            self.title or self._label("values"),
            tuple(self._columns(key) for key in keys),
            formatted,
        )

    def _scalar_section(self, items: Sequence[Any]) -> _TableSection:
        keys = [str(index + 1) for index in range(len(items))]
        if self.columns:
            keys = [key for key in keys if key in self.columns]
        row = tuple(self._format(item) for item in items[: len(keys)])
        return _TableSection(
            self.title or self._label("values"),
            tuple(self._columns(key) for key in keys),
            (row,),
        )

    def _enum_section(self, value: Enum) -> _TableSection:
        key = "scope" if isinstance(value, AccountNumberLengthScope) else "account_type"
        return _TableSection(
            self.title or self._label(key),
            (self._columns(key),),
            ((self._format(value),),),
        )

    def _group_items(self, items: Sequence[Any]) -> list[tuple[str, list[Any], type | None]]:
        groups: list[tuple[str, list[Any], type | None]] = []
        for item in items:
            if is_dataclass(item) and not isinstance(item, type):
                if groups and groups[-1][0] == "records" and groups[-1][2] is type(item):
                    groups[-1][1].append(item)
                else:
                    groups.append(("records", [item], type(item)))
            elif isinstance(item, Mapping):
                if groups and groups[-1][0] == "mappings":
                    groups[-1][1].append(item)
                else:
                    groups.append(("mappings", [item], None))
            elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                groups.append(("nested", [item], None))
            elif groups and groups[-1][0] == "scalars":
                groups[-1][1].append(item)
            else:
                groups.append(("scalars", [item], None))
        return groups

    def _rich_table(self, section: _TableSection) -> Table:
        table = Table(
            title=section.title,
            show_header=self.show_columns,
            box=box.ROUNDED,
            style="bright_white",
            border_style="bright_black",
            header_style="bold bright_cyan",
            title_style="bold bright_magenta",
            row_styles=("on #1b2130", "on #242c3e"),
            show_lines=True,
            expand=False,
            pad_edge=True,
        )
        for key, label in section.columns:
            table.add_column(
                label,
                style=COLUMN_STYLES.get(key, "white"),
                overflow="fold",
                vertical="middle",
            )
        for row in section.rows:
            table.add_row(*row)
        return table


def _resolve(view: View | None, options: dict[str, Any]) -> View:
    if view is not None:
        if options:
            raise TypeError("pass either a View or View options, not both")
        return view
    return View(**options)


def render(value: Any, *, view: View | None = None, **options: Any) -> RenderableType:
    """Return a Rich renderable for any CENIT value or collection."""
    return _resolve(view, options).render(value)


def display(
    value: Any, *, view: View | None = None, console: Console | None = None, **options: Any
) -> None:
    """Print any CENIT value or collection."""
    config = _resolve(view, options)
    config.display(value, console=console)


def explore(value: Any, *, view: View | None = None, **options: Any) -> None:
    """Open any CENIT value or collection in the Textual explorer."""
    _resolve(view, options).explore(value)


def footnote_definitions(language: str = "en") -> dict[str, str]:
    """Return footnote marker definitions in English or Spanish."""
    return dict(FOOTNOTE_DEFINITIONS[View(language=language).language])


def to_text(value: Any, *, view: View | None = None, **options: Any) -> str:
    """Render any CENIT value or collection to plain text."""
    return _resolve(view, options).to_text(value)


def to_html(value: Any, *, view: View | None = None, **options: Any) -> str:
    """Render any CENIT value or collection to HTML."""
    return _resolve(view, options).to_html(value)


def to_svg(value: Any, *, view: View | None = None, **options: Any) -> str:
    """Render any CENIT value or collection to SVG."""
    return _resolve(view, options).to_svg(value)


def save(
    value: Any,
    path: str | Path,
    *,
    view: View | None = None,
    format: str | None = None,
    **options: Any,
) -> Path:
    """Render any CENIT value or collection and write it to ``path``."""
    return _resolve(view, options).save(value, path, format=format)
