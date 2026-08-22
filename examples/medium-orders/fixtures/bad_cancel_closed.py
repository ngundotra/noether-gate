"""Cancels a shipped order. Should be deniable via cancel-only-open."""

from typing import Optional

ALLOWED = {
    ("pending", "paid"),
    ("paid", "shipped"),
    ("shipped", "delivered"),
    ("pending", "cancelled"),
    ("paid", "cancelled"),
    ("shipped", "cancelled"),
}


def transition(current: str, nxt: str) -> Optional[str]:
    if (current, nxt) in ALLOWED:
        return nxt
    return None
