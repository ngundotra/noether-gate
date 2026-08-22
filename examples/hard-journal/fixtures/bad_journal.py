"""Refunds more than charged. Should be deniable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Entry:
    kind: str
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
    # missing remaining-balance check
    return journal + [entry]
