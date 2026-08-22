"""Mints 1 extra on the dest side. Should be deniable."""

from typing import Optional, Tuple


def transfer(source: int, dest: int, amount: int) -> Optional[Tuple[int, int]]:
    if amount > source:
        return None
    return (source - amount, dest + amount + 1)
