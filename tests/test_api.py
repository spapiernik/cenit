import sys
import unittest
from datetime import date, datetime
from pathlib import Path

import cenit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_data


class ApiTest(unittest.TestCase):
    def test_get_accepts_strings_and_integers(self) -> None:
        self.assertEqual(cenit.get_by_code("1059").name, "BANCAMÍA")
        self.assertEqual(cenit.get_by_code(1059).code, "1059")

    def test_get_by_code_rejects_unknown_codes(self) -> None:
        with self.assertRaises(cenit.ParticipantNotFound):
            cenit.get_by_code("9999")
        self.assertIsNone(cenit.get_by_code("9999", default=None))
        self.assertTrue(issubclass(cenit.ParticipantNotFound, KeyError))

    def test_get_by_name_is_accent_insensitive(self) -> None:
        self.assertEqual(cenit.get_by_name("bancamia").code, "1059")
        self.assertEqual(cenit.get_by_name("BANCAMÍA").code, "1059")
        self.assertIsNone(cenit.get_by_name("not a participant", default=None))
        with self.assertRaises(cenit.ParticipantNotFound):
            cenit.get_by_name("not a participant")

    def test_get_by_name_uses_fuzzy_match(self) -> None:
        self.assertEqual(cenit.get_by_name("BANCOLOMBI").code, "1007")
        self.assertEqual(cenit.get_by_name("bamlom").code, "1007")
        self.assertEqual(cenit.get_by_name("bbva").code, "1013")
        self.assertEqual(cenit.get_by_name("bancol").code, "1007")
        self.assertIsNone(cenit.get_by_name("foo", default=None))
        self.assertIsNone(cenit.get_by_name("not found", default=None))

    def test_get_by_name_breaks_ties_by_row_number(self) -> None:
        self.assertEqual(cenit.get_by_name("banco").code, "1040")

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
        bbva = cenit.get_by_code("1013")
        self.assertTrue(bbva.supports_account_number_length("savings", 10))
        self.assertTrue(
            bbva.supports_account_number_length(cenit.AccountType.SAVINGS, 10)
        )
        self.assertFalse(bbva.supports_account_number_length("savings", 5))
        self.assertTrue(
            bbva.supports_account_number_length(
                "savings", 5, scope="special_collection_agreement"
            )
        )
        self.assertTrue(bbva.supports_account_number_length("savings", 5, scope=None))
        self.assertEqual(
            bbva.account_number_lengths("savings", scope=None),
            (5, 7, 13, 9, 10, 12, 14, 16),
        )
        self.assertEqual(bbva.account_number_lengths("savings"), (9, 10, 12, 14, 16))

    def test_participant_entity_types_are_enums(self) -> None:
        record = cenit.get_by_code("1013")
        self.assertIsInstance(record, cenit.Participant)
        self.assertIn(cenit.EntityType.BANK, record.entity_types)
        self.assertIn(cenit.EntityType.INFORMATION_OPERATOR, record.entity_types)

    def test_list_helpers(self) -> None:
        self.assertEqual(len(cenit.list_participants_by_entity_type("bank")), 27)
        self.assertEqual(len(cenit.list_debit_capable_participants()), 38)
        with self.assertRaises(ValueError):
            cenit.list_participants_by_entity_type("unknown")

    def test_sedpe_spelling_is_canonicalized(self) -> None:
        self.assertEqual(cenit.EntityType.SEDPE.value, "sedpe")
        self.assertIs(cenit.EntityType("seped"), cenit.EntityType.SEDPE)
        self.assertEqual(cenit.totals().entity_types.sedpe, 1)
        self.assertEqual(len(cenit.list_participants_by_entity_type("sedpe")), 1)
        self.assertEqual(len(cenit.list_participants_by_entity_type("seped")), 1)
        self.assertEqual(len(cenit.list_participants_by_entity_type("SEDPE")), 1)
        self.assertEqual(
            generate_data.canonicalize_entity_type_key("seped"),
            "sedpe",
        )

    def test_participant_exposes_code(self) -> None:
        self.assertEqual(cenit.get_by_code("1059").code, "1059")

    def test_footnotes_totals_and_metadata(self) -> None:
        self.assertEqual(cenit.footnotes()["(**)"], "Used for special collection agreements")
        self.assertEqual(cenit.totals().participants, 50)
        self.assertEqual(cenit.totals().entity_types.bank, 27)
        self.assertEqual(cenit.EntityType.BANK.value, "bank")
        self.assertEqual(cenit.version(), "0.1.0")
        source = cenit.source()
        self.assertIsInstance(source, cenit.Source)
        self.assertEqual(source.schema_version, 2)
        self.assertEqual(source.document_date, date(2026, 10, 7))
        self.assertIsInstance(source.fetched_at, datetime)
        self.assertEqual(
            source.sha256,
            "ee7e3775387ec9032c3eb7cb3664c63dbd7e8187bab6687f9e8cc907b4d79706",
        )
        self.assertEqual(source.url, "https://www.banrep.gov.co/sites/default/files/codigos-compensacion-cenit.pdf")

    def test_generated_module_matches_versioned_json(self) -> None:
        dataset = generate_data.read_json(generate_data.DATA_PATH)
        source = generate_data.read_json(generate_data.SOURCE_PATH)
        generated = generate_data.render_module(dataset, source, cenit.version())
        actual = generate_data.MODULE_PATH.read_text(encoding="utf-8")
        self.assertEqual(actual, generated)


if __name__ == "__main__":
    unittest.main()
