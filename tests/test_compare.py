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


if __name__ == "__main__":
    unittest.main()
