"""Pure, tested financial calculations used by database-backed reports."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping


CENT = Decimal("0.01")


def money(value) -> Decimal:
    """Normalize a financial value without binary-float rounding drift."""
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_cash_closure(real_amount, virtual_amount) -> dict[str, float]:
    """Return the specified closure difference: real minus virtual."""
    real = money(real_amount)
    virtual = money(virtual_amount)
    difference = real - virtual
    return {
        "montant_reel": float(real),
        "montant_virtuel": float(virtual),
        "difference": float(difference),
        "net": float(difference),
    }


def calculate_coffre_summary(
    cash_row: Mapping[str, object] | None,
    coffre_row: Mapping[str, object] | None,
    partner_row: Mapping[str, object] | None,
    profitability_in=0,
) -> dict[str, float]:
    """Apply the approved operational coffre formula from paid source movements.

    CA LAM is represented separately from the net coffre.  Only paid partner
    payments and approved profitability movements are accepted by callers.
    """
    cash_row = cash_row or {}
    coffre_row = coffre_row or {}
    partner_row = partner_row or {}
    caisse_cv = money(cash_row.get("caisse_cv"))
    caisse_c = money(cash_row.get("caisse_c"))
    tpe = money(cash_row.get("tpe"))
    entrees_supp = money(coffre_row.get("entrees_supp"))
    sorties = money(coffre_row.get("sorties"))
    sous_traitants = money(partner_row.get("sous_traitants_payes"))
    conventions = money(partner_row.get("conventions_payees"))
    profit = money(profitability_in)

    ca_lam = caisse_cv + caisse_c + tpe
    coffre_net = caisse_cv + caisse_c + entrees_supp + profit + sous_traitants + conventions - sorties
    global_total = coffre_net + ca_lam + conventions + sous_traitants + entrees_supp
    values = {
        "caisse_cv": caisse_cv,
        "caisse_c": caisse_c,
        "tpe": tpe,
        "ca_lam": ca_lam,
        "ca_convention": conventions,
        "ca_st": sous_traitants,
        "ca_supp": entrees_supp,
        "mouvement_profitabilite": profit,
        "total_sorties": sorties,
        "coffre_net": coffre_net,
        "global": global_total,
    }
    return {name: float(amount) for name, amount in values.items()}
