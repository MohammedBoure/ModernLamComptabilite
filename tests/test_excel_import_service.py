import sys
import unittest
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from services.excel_import_service import (  # noqa: E402
    build_row_payload,
    find_header_row,
    reconciliation_from_payloads,
)


class ExcelImportServiceTests(unittest.TestCase):
    def test_finds_first_reliable_header_row(self):
        header_row, headers = find_header_row(
            [("MODERNLAM", None), ("Date", "Montant", "Notes"), (date(2026, 1, 1), 10, "ok")]
        )
        self.assertEqual(header_row, 2)
        self.assertEqual(headers[0], "Date")

    def test_payload_keeps_exact_source_provenance(self):
        payload = build_row_payload(
            "Etat.xlsx", "Feuil1", 7, ["Date", "Montant", "Formule"], [date(2026, 1, 2), 12.5, "=SUM(B1:B6)"]
        )
        self.assertEqual(payload["source"]["filename"], "Etat.xlsx")
        self.assertEqual(payload["source"]["sheet"], "Feuil1")
        self.assertEqual(payload["source"]["row"], 7)
        self.assertEqual(payload["values"]["Date"], "2026-01-02")
        self.assertEqual(payload["values"]["Formule"], "=SUM(B1:B6)")

    def test_reconciliation_does_not_turn_formulas_into_source_values(self):
        payloads = [
            build_row_payload("a.xlsx", "Sheet", 2, ["Montant", "Total"], [10, "=SUM(A1:A2)"]),
            build_row_payload("a.xlsx", "Sheet", 3, ["Montant", "Total"], [12.5, None]),
        ]
        summary = reconciliation_from_payloads(payloads)
        self.assertEqual(summary["row_count"], 2)
        self.assertEqual(summary["numeric_totals"], {"Montant": 22.5})


if __name__ == "__main__":
    unittest.main()
