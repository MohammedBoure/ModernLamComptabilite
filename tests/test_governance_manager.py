import sys
import unittest
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "database"))
from governance_manager import GovernanceManager, PeriodLockedError
from financial_calculations import calculate_cash_closure, calculate_coffre_summary


class FakeDatabase:
    def __init__(self, period=None, policy=True, cash_gaps=0, drafts=0, role="ADMIN"):
        self.period = period or {"id_period": 7, "annee": 2026, "mois": 1, "status": "OPEN"}
        self.policy = policy
        self.cash_gaps = cash_gaps
        self.drafts = drafts
        self.role = role
        self.commands = []

    def fetch_one(self, query, params=None):
        if "Accounting_Periods WHERE annee" in query:
            return self.period
        if "Accounting_Periods WHERE id_period" in query:
            return self.period
        if "Utilisateurs" in query:
            return {"role_code": self.role, "is_active": 1}
        if "Calculation_Policies" in query:
            return {"id_policy": 1} if self.policy else None
        if "Cloture_Caisse" in query:
            return {"count": self.cash_gaps}
        if "Fiches_Paie" in query:
            return {"count": self.drafts}
        raise AssertionError(f"Unexpected query: {query}")

    def execute(self, query, params=None):
        self.commands.append((query, params))
        return True, len(self.commands)


class GovernanceManagerTests(unittest.TestCase):
    def test_writable_period_accepts_open_period(self):
        manager = GovernanceManager(FakeDatabase())
        period = manager.assert_writable_period("2026-01-15", "admin")
        self.assertEqual(period["id_period"], 7)

    def test_writable_period_rejects_locked_period(self):
        database = FakeDatabase(period={"id_period": 7, "annee": 2026, "mois": 1, "status": "CLOSED"})
        with self.assertRaises(PeriodLockedError):
            GovernanceManager(database).assert_writable_period(date(2026, 1, 15))

    def test_viewer_cannot_write_in_an_open_period(self):
        database = FakeDatabase(role="VIEWER")
        with self.assertRaises(PermissionError):
            GovernanceManager(database).assert_writable_period("2026-01-15", "viewer")
    def test_close_requires_approved_policy(self):
        database = FakeDatabase(policy=False)
        with self.assertRaisesRegex(ValueError, "approved financial"):
            GovernanceManager(database).close_period(7, "admin")

    def test_close_rejects_unexplained_cash_difference(self):
        database = FakeDatabase(cash_gaps=1)
        with self.assertRaisesRegex(ValueError, "cash differences"):
            GovernanceManager(database).close_period(7, "admin")

    def test_close_writes_period_and_audit_event(self):
        database = FakeDatabase()
        self.assertTrue(GovernanceManager(database).close_period(7, "admin", "monthly close"))
        self.assertEqual(len(database.commands), 2)
        self.assertIn("UPDATE Accounting_Periods", database.commands[0][0])
        self.assertIn("INSERT INTO Audit_Events", database.commands[1][0])

    def test_reopen_requires_admin_and_reason(self):
        non_admin = GovernanceManager(FakeDatabase(role="ACCOUNTANT"))
        with self.assertRaises(PermissionError):
            non_admin.reopen_period(7, "accountant", "correction")
        admin = GovernanceManager(FakeDatabase())
        with self.assertRaises(ValueError):
            admin.reopen_period(7, "admin", "")


    def test_cash_closure_uses_real_minus_virtual_for_difference_and_net(self):
        closure = calculate_cash_closure("120.50", "100.25")
        self.assertEqual(closure["difference"], 20.25)
        self.assertEqual(closure["net"], 20.25)

    def test_coffre_formula_uses_paid_sources_and_profitability(self):
        result = calculate_coffre_summary(
            {"caisse_cv": 100, "caisse_c": 200, "tpe": 50},
            {"entrees_supp": 40, "sorties": 70},
            {"sous_traitants_payes": 30, "conventions_payees": 20},
            profitability_in=10,
        )
        self.assertEqual(result["ca_lam"], 350.0)
        self.assertEqual(result["coffre_net"], 330.0)
        self.assertEqual(result["global"], 770.0)
if __name__ == "__main__":
    unittest.main()
