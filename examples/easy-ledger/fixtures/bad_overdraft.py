"""Accepts an overdraft as a no-op. Should be deniable via no-overdraft."""

from typing import Optional, Tuple


def transfer(source: int, dest: int, amount: int) -> Optional[Tuple[int, int]]:
    if amount > source:
        return (source, dest)
    return (source - amount, dest + amount)
