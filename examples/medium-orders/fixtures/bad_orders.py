"""Skips paid: pending can jump to shipped. Should be deniable."""

from typing import Optional

ALLOWED = {
    ("pending", "paid"),
    ("pending", "shipped"),
    ("paid", "shipped"),
    ("shipped", "delivered"),
    ("pending", "cancelled"),
    ("paid", "cancelled"),
}


def transition(current: str, nxt: str) -> Optional[str]:
    if (current, nxt) in ALLOWED:
        return nxt
    return None
