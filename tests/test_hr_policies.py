import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "database"))
from hr_policies import leave_accrual_days, leave_accrual_months  # noqa: E402


class LeaveAccrualTests(unittest.TestCase):
    def test_hire_on_fifteenth_accrues_the_hire_month(self):
        self.assertEqual(leave_accrual_months(date(2026, 9, 15), 2026), 4)
        self.assertEqual(leave_accrual_days(date(2026, 9, 15), 2026), Decimal("10.00"))

    def test_hire_after_fifteenth_starts_next_month(self):
        self.assertEqual(leave_accrual_months(date(2026, 9, 16), 2026), 3)
        self.assertEqual(leave_accrual_days(date(2026, 9, 16), 2026), Decimal("7.50"))

    def test_prior_year_hire_accrues_all_year_and_future_hire_none(self):
        self.assertEqual(leave_accrual_months(date(2025, 12, 30), 2026), 12)
        self.assertEqual(leave_accrual_months(date(2027, 1, 1), 2026), 0)


if __name__ == "__main__":
    unittest.main()
