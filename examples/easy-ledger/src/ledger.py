"""Tiny product. Lean model: examples/easy-ledger/lean/EasyLedger/Statements.lean."""

from typing import Optional, Tuple


def transfer(source: int, dest: int, amount: int) -> Optional[Tuple[int, int]]:
    if amount > source:
        return None
    return (source - amount, dest + amount)
