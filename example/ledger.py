"""Tiny product. The Lean model in lean/Noether/Ledger.lean must stay in sync."""

from typing import Optional, Tuple


def transfer(source: int, dest: int, amount: int) -> Optional[Tuple[int, int]]:
    if amount > source:
        return None
    return (source - amount, dest + amount)
