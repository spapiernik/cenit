import json
import sys
import unittest
from pathlib import Path

import cenit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare


class ExtractorTest(unittest.TestCase):
    def test_fixture_matches_committed_dataset(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "cenit_codes.pdf"
        golden = json.loads(
            (ROOT / "data" / "current" / "cenit.json").read_text(
                encoding="utf-8"
            )
        )
        result = cenit.extract(fixture, 1, None)

        self.assertEqual(cenit.SCHEMA_VERSION, 2)
        self.assertEqual(len(result["records"]), cenit.EXPECTED_PARTICIPANTS)
        self.assertEqual(result["report"]["status"], "ok")
        current = {
            "participants": result["records"],
            "totals": result["totals"],
        }
        self.assertFalse(compare.compare(golden, current)["changed"])

    def test_totals_label_detection(self) -> None:
        self.assertTrue(cenit.is_totals_label("TOTAL PARTICIPANTES EN CENIT"))
        self.assertTrue(cenit.is_totals_label("  TOTAL   PARTICIPANTES EN CENIT  "))
        self.assertFalse(cenit.is_totals_label("TOTAL PARTICIPANTES"))


if __name__ == "__main__":
    unittest.main()
