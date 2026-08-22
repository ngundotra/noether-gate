"""Charge/refund journal. Lean model: examples/hard-journal/lean/HardJournal/Statements.lean."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Entry:
    kind: str  # "charge" | "refund"
    account: int
    amount: int
    id: int
    charge_id: int


def apply(journal: List[Entry], entry: Entry) -> Optional[List[Entry]]:
    if entry.kind == "charge":
        if entry.amount == 0:
            return None
        return journal + [entry]
    charges = [e for e in journal if e.kind == "charge" and e.id == entry.charge_id]
    if not charges:
        return None
    charge = charges[0]
    if charge.account != entry.account:
        return None
    prior = sum(e.amount for e in journal if e.kind == "refund" and e.charge_id == entry.charge_id)
    if prior + entry.amount > charge.amount:
        return None
    return journal + [entry]


def sum_refunds(account: int, xs: List[Entry]) -> int:
    return sum(e.amount for e in xs if e.account == account and e.kind == "refund")


def sum_charges(account: int, xs: List[Entry]) -> int:
    return sum(e.amount for e in xs if e.account == account and e.kind == "charge")
