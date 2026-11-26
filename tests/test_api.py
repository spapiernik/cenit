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
        self.assertEqual(cenit.get_by_code("1059").participant_name, "BANCAMÍA")
        self.assertEqual(cenit.get_by_code(1059).cenit_code, "1059")
        self.assertIsNone(cenit.get_by_code("9999"))

    def test_get_or_raise_rejects_unknown_codes(self) -> None:
        self.assertEqual(cenit.get_by_code_or_raise(1059).cenit_code, "1059")
        with self.assertRaises(KeyError):
            cenit.get_by_code_or_raise("9999")

    def test_get_by_name_is_accent_insensitive(self) -> None:
        self.assertEqual(cenit.get_by_name("bancamia").cenit_code, "1059")
        self.assertEqual(cenit.get_by_name("BANCAMÍA").cenit_code, "1059")
        self.assertIsNone(cenit.get_by_name("not a participant"))

    def test_all_returns_immutable_tuple(self) -> None:
        records = cenit.all_records()
        self.assertIsInstance(records, tuple)
        self.assertEqual(len(records), 50)
        self.assertIs(records, cenit.all_records())

    def test_operation_start_date_and_note_are_separate(self) -> None:
        dated = cenit.get_by_code("1899")
        self.assertEqual(dated.operation_start_date, date(2025, 7, 3))
        self.assertIsNone(dated.operation_start_note)
        self.assertEqual(dated.footnotes, ())

        noted = cenit.get_by_code("1013")
        self.assertIsNone(noted.operation_start_date)
        self.assertEqual(noted.operation_start_note, "(*)")
        self.assertIn("(*)", noted.footnotes)

    def test_special_collection_agreement_variants(self) -> None:
        bbva = cenit.get_by_code("1013")
        savings = bbva.account_capabilities.savings_account_number_lengths
        self.assertEqual(len(savings), 2)
        self.assertEqual(savings[0].lengths, (5, 7, 13))
        self.assertEqual(savings[0].footnote_markers, ("**",))
        self.assertEqual(
            savings[0].scope,
            cenit.AccountNumberLengthScope.SPECIAL_COLLECTION_AGREEMENT,
        )
        self.assertEqual(savings[1].lengths, (9, 10, 12, 14, 16))
        self.assertEqual(savings[1].scope, cenit.AccountNumberLengthScope.STANDARD)

        checking = bbva.account_capabilities.checking_account_number_lengths
        self.assertEqual(checking[0].lengths, (5, 7))
        self.assertEqual(checking[0].footnote_markers, ("**",))
        self.assertIn("(**)", bbva.footnotes)

    def test_includes_leading_zeros_variant(self) -> None:
        lulo = cenit.get_by_code("1070")
        variants = lulo.account_capabilities.savings_account_number_lengths
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0].lengths, (12,))
        self.assertEqual(variants[0].footnote_markers, ("***",))
        self.assertEqual(
            variants[0].scope, cenit.AccountNumberLengthScope.INCLUDES_LEADING_ZEROS
        )
        self.assertIn("(***)", lulo.footnotes)

    def test_electronic_deposit_not_enabled_variant(self) -> None:
        bancamia = cenit.get_by_code("1059")
        variants = (
            bancamia.account_capabilities.electronic_or_low_value_deposit_number_lengths
        )
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0].lengths, ())
        self.assertEqual(variants[0].footnote_markers, ("****",))
        self.assertEqual(
            variants[0].scope,
            cenit.AccountNumberLengthScope.ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT,
        )
        self.assertIn("(****)", bancamia.footnotes)

    def test_account_length_queries(self) -> None:
        self.assertTrue(cenit.is_valid_account_number_length("1013", "savings", 10))
        self.assertFalse(cenit.is_valid_account_number_length("1013", "savings", 5))
        self.assertTrue(
            cenit.is_valid_account_number_length(
                "1013",
                "savings",
                5,
                scope="special_collection_agreement",
            )
        )
        self.assertEqual(
            cenit.list_account_number_lengths("1013", "savings"),
            (5, 7, 13, 9, 10, 12, 14, 16),
        )
        self.assertEqual(
            cenit.list_account_number_lengths("1013", "savings", scope="standard"),
            (9, 10, 12, 14, 16),
        )

    def test_list_helpers(self) -> None:
        self.assertEqual(len(cenit.list_participants_by_entity_type("bank")), 27)
        self.assertEqual(len(cenit.list_debit_capable_participants()), 38)
        with self.assertRaises(ValueError):
            cenit.list_participants_by_entity_type("unknown")

    def test_routing_code_accepts_full_and_participant_codes(self) -> None:
        record = cenit.get_by_code("1059")
        self.assertEqual(record.participant_code, "059")
        self.assertEqual(record.routing_code, "1059")
        self.assertEqual(cenit.routing_code(1059), "1059")
        self.assertEqual(cenit.routing_code("059"), "1059")
        self.assertIsNone(cenit.routing_code("9999"))

    def test_footnotes_totals_and_metadata(self) -> None:
        self.assertEqual(cenit.footnotes()["(**)"], "Used for special collection agreements")
        self.assertEqual(cenit.totals().participants, 50)
        self.assertEqual(cenit.totals().entity_types.bank, 27)
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
