"""Reviewed HR policy calculations kept outside the UI."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def leave_accrual_months(hire_date: date, year: int) -> int:
    """Months accruing leave under the day-15 rule used by the existing DRH file.

    A hire on or before the 15th accrues that month; a hire after the 15th
    begins accruing from the following month.  Earlier hires accrue all year.
    """
    if hire_date.year > year:
        return 0
    if hire_date.year < year:
        return 12
    first_month = hire_date.month if hire_date.day <= 15 else hire_date.month + 1
    return max(0, 13 - first_month)


def leave_accrual_days(hire_date: date, year: int, monthly_days=Decimal("2.5")) -> Decimal:
    amount = Decimal(str(monthly_days)) * leave_accrual_months(hire_date, year)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
