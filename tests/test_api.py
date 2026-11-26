import sys
import unittest
from datetime import date
from pathlib import Path

import cenit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_data


class ApiTest(unittest.TestCase):
    def test_get_accepts_strings_and_integers(self) -> None:
        self.assertEqual(cenit.get("1059").participant, "BANCAMÍA")
        self.assertEqual(cenit.get(1059).cenit_code, "1059")
        self.assertIsNone(cenit.get("9999"))

    def test_get_or_raise_rejects_unknown_codes(self) -> None:
        self.assertEqual(cenit.get_or_raise(1059).cenit_code, "1059")
        with self.assertRaises(KeyError):
            cenit.get_or_raise("9999")

    def test_find_by_name_is_accent_insensitive(self) -> None:
        self.assertEqual(cenit.find_by_name("bancamia").cenit_code, "1059")
        self.assertEqual(cenit.find_by_name("BANCAMÍA").cenit_code, "1059")
        self.assertIsNone(cenit.find_by_name("not a participant"))

    def test_all_returns_immutable_tuple(self) -> None:
        records = cenit.all()
        self.assertIsInstance(records, tuple)
        self.assertEqual(len(records), 50)
        self.assertEqual(cenit.all_codes(), records)

    def test_typed_record_fields(self) -> None:
        record = cenit.get("1899")
        self.assertEqual(record.operation_start_date, date(2025, 7, 3))
        self.assertEqual(record.operation_start_label, "3/07/2025")
        self.assertEqual(record.entity_types, ("seped",))
        self.assertTrue(record.supports_debit_transactions)
        self.assertEqual(record.electronic_or_low_value_deposit, "DALE")

        bbva = cenit.get("1013")
        self.assertEqual(bbva.entity_types, ("bank", "information_operator"))
        self.assertEqual(
            bbva.account_types.savings_account_lengths,
            (5, 7, 13, 9, 10, 12, 14, 16),
        )
        self.assertEqual(
            bbva.account_types.checking_account_lengths,
            (5, 7, 9, 10, 12, 14, 16),
        )
        self.assertEqual(bbva.electronic_or_low_value_deposit, "DINERO MOVIL")

    def test_routing_code_accepts_full_and_participant_codes(self) -> None:
        record = cenit.get("1059")
        self.assertEqual(record.participant_code, "059")
        self.assertEqual(record.routing_code, "1059")
        self.assertEqual(cenit.routing_code(1059), "1059")
        self.assertEqual(cenit.routing_code("059"), "1059")
        self.assertIsNone(cenit.routing_code("9999"))

    def test_totals_and_metadata(self) -> None:
        self.assertEqual(cenit.totals().participants, 50)
        self.assertEqual(cenit.totals().entity_types["bank"], 27)
        self.assertEqual(cenit.ENTITY_TYPES[0], "bank")
        self.assertEqual(cenit.version(), "0.1.0")
        self.assertEqual(cenit.schema_version(), 2)
        self.assertEqual(cenit.source_date(), date(2026, 10, 7))
        self.assertEqual(
            cenit.source_sha256(),
            "ee7e3775387ec9032c3eb7cb3664c63dbd7e8187bab6687f9e8cc907b4d79706",
        )

    def test_generated_module_matches_versioned_json(self) -> None:
        dataset = generate_data.read_json(generate_data.DATA_PATH)
        source = generate_data.read_json(generate_data.SOURCE_PATH)
        generated = generate_data.render_module(dataset, source, cenit.version())
        actual = generate_data.MODULE_PATH.read_text(encoding="utf-8")
        self.assertEqual(actual, generated)


if __name__ == "__main__":
    unittest.main()
