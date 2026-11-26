import asyncio
import tempfile
import unittest
from pathlib import Path

import cenit
from cenit._tui import CenitExplorer
from rich.style import Style


def header_line(text: str) -> str:
    return next(line for line in text.splitlines() if "│" in line and "Participant" in line)


def header_block(text: str) -> str:
    lines = text.splitlines()
    start = lines.index(header_line(text))
    collected: list[str] = []
    for line in lines[start:]:
        if "│" not in line:
            break
        collected.append(line)
    return "\n".join(collected)


class ViewTest(unittest.TestCase):
    def test_record_render_includes_default_columns(self) -> None:
        text = cenit.to_text(cenit.get_by_code("1013"), width=400)
        header = header_block(text)
        self.assertIn("ParticipantRecord", text)
        self.assertIn("BANCO BBVA", text)
        self.assertIn("1013", text)
        self.assertIn("CENIT Compensation Code", header)
        self.assertIn("Operation Start", header)
        self.assertIn("Applies Debit Transactions", header)
        self.assertNotIn("Footnotes", header)
        self.assertIn("Linked before May 2025", text)

    def test_spanish_labels(self) -> None:
        text = cenit.to_text(cenit.get_by_code("1013"), language="es", width=400)
        self.assertIn("Participante", header_block(text))
        self.assertIn("Código de Compensación CENIT", text)
        self.assertIn("Inicio de Operación", text)
        self.assertIn("Aplica Transacciones Débito", text)
        self.assertIn("Vinculación antes de mayo de 2025", text)
        row = next(line for line in text.splitlines() if "BANCO BBVA" in line)
        self.assertIn("Banco, Operador de Información", row)

    def test_boolean_values_are_not_inverted(self) -> None:
        records = cenit.all_records()
        true_record = next(record for record in records if record.supports_debit_transactions)
        false_record = next(record for record in records if not record.supports_debit_transactions)
        text = cenit.to_text(
            [true_record, false_record],
            columns=("participant_name", "supports_debit_transactions"),
            show_footnotes=False,
            width=200,
        )
        self.assertIn("yes", text)
        self.assertIn("no", text)

    def test_row_stripes_use_backgrounds_only(self) -> None:
        view = cenit.View(width=200)
        table = view._rich_table(view.sections(cenit.get_by_code("1013"))[0])
        styles = [Style.parse(item) for item in table.row_styles]
        self.assertTrue(styles)
        self.assertTrue(all(style.color is None for style in styles))
        self.assertTrue(all(style.bgcolor is not None for style in styles))

    def test_operation_start_uses_note_when_no_date(self) -> None:
        text = cenit.to_text(
            cenit.get_by_code("1013"), show_footnotes=False, width=200
        )
        row = next(line for line in text.splitlines() if "BANCO BBVA" in line)
        self.assertIn("(*)", row)
        self.assertNotIn("Operation Start Note", header_line(text))

    def test_language_aliases(self) -> None:
        self.assertEqual(cenit.View(language="spa").language, "es")
        self.assertEqual(cenit.View(language="ENG").language, "en")
        self.assertEqual(
            cenit.footnote_definitions("spa")["(*)"],
            "Vinculación antes de mayo de 2025",
        )
        with self.assertRaises(ValueError):
            cenit.View(language="fr")

    def test_columns_exclude_and_header_toggle(self) -> None:
        record = cenit.get_by_code("1013")
        selected = cenit.to_text(
            record,
            columns=("participant_name", "cenit_code"),
            width=200,
        )
        self.assertIn("CENIT Compensation Code", header_line(selected))
        self.assertNotIn("Footnotes", header_line(selected))

        hidden = cenit.to_text(
            record,
            columns=("participant_name", "cenit_code"),
            show_columns=False,
            width=200,
        )
        self.assertNotIn("CENIT Compensation Code", hidden)
        self.assertIn("1013", hidden)

    def test_keep_excluded_columns(self) -> None:
        text = cenit.to_text(
            cenit.get_by_code("1013"),
            columns=("participant_name", "footnotes"),
            exclude=("footnotes",),
            keep_excluded_columns=True,
            show_footnotes=False,
            width=200,
        )
        self.assertIn("Footnotes", header_line(text))

    def test_row_columns_override(self) -> None:
        records = [cenit.get_by_code("1013"), cenit.get_by_code("1070")]
        text = cenit.to_text(
            records,
            columns=("participant_name",),
            row_columns={1: ("cenit_code",)},
            show_footnotes=False,
            width=200,
        )
        self.assertIn("BANCO BBVA", text)
        row = next(line for line in text.splitlines() if "1070" in line)
        self.assertNotIn("BANCO BBVA", row)

    def test_nested_dataclasses_expand_into_columns(self) -> None:
        text = cenit.to_text(cenit.totals(), width=200)
        self.assertNotIn("EntityTypeTotals(", text)
        for label in (
            "Banks",
            "Financial Cooperative",
            "Financial Corporation",
            "Financing Company",
            "Government Entity",
            "Information Operator",
            "SEPED",
        ):
            self.assertIn(label, text)

    def test_account_subcolumns(self) -> None:
        text = cenit.to_text(cenit.get_by_code("1013"), language="es", width=400)
        header = header_block(text)
        for label in (
            "Cuenta de Ahorros",
            "Cuenta Corriente",
            "Depósito Electrónico o de Bajo Monto",
            "Nombre del Depósito Electrónico o de Bajo Monto",
        ):
            self.assertIn(label, header)
        row = next(line for line in text.splitlines() if "BANCO BBVA" in line)
        self.assertIn("5, 7, 13", row)
        self.assertIn("DINERO MOVIL", row)

    def test_footnotes_are_ordered(self) -> None:
        text = cenit.to_text(cenit.all_records(), width=400)
        block = text.split("Footnotes", 1)[1]
        definitions = cenit.footnote_definitions()
        positions = [block.index(definition) for definition in definitions.values()]
        self.assertEqual(positions, sorted(positions))

    def test_textual_explorer_builds_tables(self) -> None:
        async def check() -> None:
            app = CenitExplorer(
                cenit.View(width=160), [cenit.get_by_code("1013"), cenit.totals()]
            )
            async with app.run_test():
                self.assertEqual(len(list(app.query("DataTable"))), 2)

        asyncio.run(check())

    def test_mixed_collections_have_separators(self) -> None:
        text = cenit.to_text(
            [cenit.get_by_code("1013"), cenit.totals()],
            width=200,
        )
        self.assertIn("ParticipantRecord", text)
        self.assertIn("Totals", text)
        self.assertIn("─", text)

    def test_nested_collections(self) -> None:
        record = cenit.get_by_code("1013")
        text = cenit.to_text([record, [record, cenit.totals()]], width=200)
        self.assertEqual(text.count("ParticipantRecord"), 2)
        self.assertIn("Totals", text)

    def test_cells_and_matrices(self) -> None:
        self.assertIn("7", cenit.to_text([7, 8], width=80))
        matrix = cenit.to_text([[1, 2], [3, 4]], width=80)
        self.assertIn("1", matrix)
        self.assertIn("4", matrix)

    def test_exports_and_save(self) -> None:
        record = cenit.get_by_code("1013")
        html = cenit.to_html(record, width=200)
        self.assertIn("<html", html)
        self.assertIn("BANCO BBVA", html)
        self.assertIn("<svg", cenit.to_svg(record))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "record.html"
            returned = cenit.save(record, target, width=200)
            self.assertEqual(returned, target)
            self.assertIn("<html", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
