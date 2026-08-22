"""Accepts a refund with no matching charge. Should be deniable via refunds-reference-charge."""

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
    return journal + [entry]
