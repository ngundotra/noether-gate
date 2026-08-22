"""Tiny product. Lean model: examples/easy-ledger/lean/EasyLedger/Statements.lean."""

from typing import Optional, Tuple


def transfer(source: int, dest: int, amount: int, retries: int = 0) -> Optional[Tuple[int, int]]:
    if amount > source:
        return None
    src, dst = source - amount, dest + amount
    # New: retry the send if the caller asked. Each retry sends again.
    for _ in range(retries):
        if amount > src:
            break
        src -= amount
        dst += amount
    return (src, dst)
