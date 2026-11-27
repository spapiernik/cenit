import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare
import extract


class ExtractorTest(unittest.TestCase):
    def test_change_log_parser_groups_wrapped_entries(self) -> None:
        text = """\
        CONTROL DE CAMBIOS
        27 de noviembre de 2026 - Se incluye a NU COLOMBIA COMPAÑÍA DE
        FINANCIAMIENTO S.A. como entidad autorizada en el Sistema CENIT.
        - Se corrige la sigla SEPED por SEDPE.
        7 de octubre de 2026 - Se incluye el nombre de BANCOLOMBIA.
        Hoja 2 de 2
        """
        entries = extract.parse_change_log(text)

        self.assertEqual(
            entries[0],
            {
                "date": "2026-11-27",
                "text": (
                    "Se incluye a NU COLOMBIA COMPAÑÍA DE FINANCIAMIENTO S.A. "
                    "como entidad autorizada en el Sistema CENIT."
                ),
            },
        )
        self.assertEqual(entries[1]["date"], "2026-11-27")
        self.assertIn("SEPED por SEDPE", entries[1]["text"])
        self.assertEqual(entries[2]["date"], "2026-10-07")

    def test_fixture_matches_committed_dataset(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "cenit_codes.pdf"
        golden = json.loads(
            (ROOT / "data" / "current" / "cenit.json").read_text(
                encoding="utf-8"
            )
        )
        result = extract.extract(fixture, 1, None)

        self.assertEqual(extract.SCHEMA_VERSION, 2)
        self.assertEqual(
            result["report"]["summary"]["declared_participants"],
            len(result["records"]),
        )
        recorded_source = json.loads(
            (ROOT / "data" / "source.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            result["source"]["document_date"], recorded_source["document_date"]
        )
        self.assertEqual(result["report"]["status"], "ok")
        current = {
            "participants": result["records"],
            "totals": result["totals"],
        }
        self.assertFalse(compare.compare(golden, current)["changed"])

    def test_totals_label_detection(self) -> None:
        self.assertTrue(extract.is_totals_label("TOTAL PARTICIPANTES EN CENIT"))
        self.assertTrue(extract.is_totals_label("  TOTAL   PARTICIPANTES EN CENIT  "))
        self.assertFalse(extract.is_totals_label("TOTAL PARTICIPANTES"))

    def test_sedpe_spelling_is_canonicalized(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "cenit_codes.pdf"
        result = extract.extract(fixture, 1, None)
        payload = json.dumps(result, ensure_ascii=False).lower()

        self.assertNotIn("seped", payload)
        self.assertIn("sedpe", result["totals"]["tipo_de_entidad"])
        self.assertTrue(
            any("sedpe" in record["tipo_de_entidad"] for record in result["records"])
        )
        self.assertEqual(extract.canonicalize_sedpe("seped"), "SEDPE")
        self.assertEqual(extract.canonicalize_sedpe("SEDPE"), "SEDPE")


if __name__ == "__main__":
    unittest.main()
