import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare


def record(code: str, name: str, position: int = 1) -> dict:
    return {
        "posición": position,
        "participante": name,
        "código_cenit": code,
        "tipo_de_entidad": {"bancos": True, "sedpe": False},
    }


class CompareTest(unittest.TestCase):
    def test_detects_semantic_changes_only(self) -> None:
        previous = {
            "source": {"sha256": "old"},
            "participants": [record("1000", "OLD S.A."), record("1001", "KEEP S.A.")],
            "totals": {"participantes": "50", "tipo_de_entidad": {"bancos": "27"}},
        }
        current = {
            "source": {"sha256": "new"},
            "participants": [record("1000", "NEW S.A.", 7), record("1002", "ADDED S.A.")],
            "totals": {"participantes": "50", "tipo_de_entidad": {"bancos": "28"}},
        }

        result = compare.compare(previous, current)

        self.assertTrue(result["changed"])
        self.assertEqual(result["added"], ["1002"])
        self.assertEqual(result["removed"], ["1001"])
        self.assertEqual(result["changed_participants"][0]["code"], "1000")
        self.assertEqual(
            result["changed_participants"][0]["fields"][0]["path"], "participante"
        )
        self.assertEqual(result["totals_changes"][0]["path"], "tipo_de_entidad.bancos")
        self.assertNotIn("posición", str(result["changed_participants"]))

    def test_identical_data_after_key_normalization(self) -> None:
        previous = {"participants": [record("1000", "NAME")], "totals": {"sedpe": "1"}}
        current = {"participants": [record("1000", "NAME", 99)], "totals": {"sedpe": "1"}}

        result = compare.compare(previous, current)

        self.assertFalse(result["changed"])
        self.assertIn("No changes", compare.render_markdown(result))

    def test_render_includes_provenance_names_and_recent_change_log(self) -> None:
        previous = {
            "source": {"sha256": "old", "document_date": "2026-10-07"},
            "participants": [record("1000", "KEEP S.A.")],
            "totals": {
                "participantes": "1",
                "tipo_de_entidad": {"compañía_de_financiamiento": "0"},
            },
        }
        added = record("1002", "ADDED S.A.")
        added["inicio_de_operación"] = "1/12/2026"
        added["tipo_de_entidad"] = {"compañía_de_financiamiento": True}
        current = {
            "source": {
                "sha256": "new",
                "document_date": "2026-11-27",
                "url": "https://example.test/cenit.pdf",
            },
            "participants": [record("1000", "KEEP S.A."), added],
            "totals": {
                "participantes": "2",
                "tipo_de_entidad": {"compañía_de_financiamiento": "1"},
            },
        }
        previous_report = {"change_log": []}
        current_report = {
            "change_log": [
                {"date": "2026-11-27", "text": "Se incluye a ADDED S.A."},
                {"date": "2026-10-07", "text": "Old entry"},
            ]
        }

        result = compare.compare(previous, current, previous_report, current_report)
        body = compare.render_markdown(result)

        self.assertIn("# CENIT table sync - 27 Nov 2026", body)
        self.assertIn("[official PDF](https://example.test/cenit.pdf)", body)
        self.assertIn("## Added Participants", body)
        self.assertIn(
            "| CENIT Compensation Code | Participant | Operation Start | Entity Type |",
            body,
        )
        self.assertIn("| 1002 | ADDED S.A. | 1/12/2026 | Financing Company |", body)
        self.assertIn("| Entity Type / Financing Company | `0` | `1` |", body)
        self.assertIn("Se incluye a ADDED S.A.", body)
        self.assertNotIn("Old entry", body)

    def test_large_changed_sections_are_collapsed(self) -> None:
        before = record("1000", "KEEP S.A.")
        after = record("1000", "KEEP S.A.")
        for index in range(11):
            before[f"field_{index}"] = f"old_{index}"
            after[f"field_{index}"] = f"new_{index}"

        result = compare.compare(
            {"participants": [before], "totals": {}},
            {"participants": [after], "totals": {}},
        )
        body = compare.render_markdown(result)

        self.assertIn("<summary>Show 11 field changes</summary>", body)
        self.assertIn("</details>", body)


if __name__ == "__main__":
    unittest.main()
