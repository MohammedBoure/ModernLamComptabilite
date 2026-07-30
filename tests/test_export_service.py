import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from services.export_service import ExportService  # noqa: E402


class FakeDatabase:
    current_actor = "accountant"

    def __init__(self):
        self.commands = []

    def execute(self, query, params=None):
        self.commands.append((query, params))
        return True, len(self.commands)

    def fetch_one(self, query, params=None):
        return {"id_period": 8}


class ExportServiceTests(unittest.TestCase):
    def test_csv_export_writes_and_records_an_audit_event(self):
        database = FakeDatabase()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "etat.csv"
            ExportService(database).export_csv(
                output, [{"Date": "2026-01-01", "Montant": 15}], "Etat Encaissement", period_id=8
            )
            self.assertTrue(output.is_file())
            self.assertIn("Montant", output.read_text(encoding="utf-8-sig"))
        self.assertEqual(len(database.commands), 2)
        self.assertIn("Export_History", database.commands[0][0])
        self.assertEqual("REPORT_EXPORTED", database.commands[1][1][1])

    def test_period_lookup_is_optional(self):
        service = ExportService(FakeDatabase())
        self.assertIsNone(service.period_id_for())
        self.assertEqual(service.period_id_for(1, 2026), 8)


if __name__ == "__main__":
    unittest.main()
