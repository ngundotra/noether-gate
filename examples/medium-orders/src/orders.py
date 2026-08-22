"""Order state machine. Lean model: examples/medium-orders/lean/MediumOrders/Statements.lean."""

from typing import Optional

STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")

ALLOWED = {
    ("pending", "paid"),
    ("paid", "shipped"),
    ("shipped", "delivered"),
    ("pending", "cancelled"),
    ("paid", "cancelled"),
}


def transition(current: str, nxt: str) -> Optional[str]:
    if (current, nxt) in ALLOWED:
        return nxt
    return None
