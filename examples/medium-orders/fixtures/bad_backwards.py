"""Moves paid back to pending. Should be deniable via no-backwards."""

from typing import Optional

ALLOWED = {
    ("pending", "paid"),
    ("paid", "shipped"),
    ("paid", "pending"),
    ("shipped", "delivered"),
    ("pending", "cancelled"),
    ("paid", "cancelled"),
}


def transition(current: str, nxt: str) -> Optional[str]:
    if (current, nxt) in ALLOWED:
        return nxt
    return None
