"""Witness search + Lean certificate for medium-orders."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PKG = "MediumOrders"
STATEMENTS = "MediumOrders/Statements.lean"
DEFAULT_IMPL = "src/orders.py"
BAD_IMPL = "fixtures/bad_orders.py"

STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")
SKIP = {
    ("pending", "shipped"),
    ("pending", "delivered"),
    ("paid", "delivered"),
}
BACKWARDS = {
    ("paid", "pending"),
    ("shipped", "pending"),
    ("shipped", "paid"),
    ("delivered", "pending"),
    ("delivered", "paid"),
    ("delivered", "shipped"),
    ("cancelled", "pending"),
    ("cancelled", "paid"),
    ("cancelled", "shipped"),
    ("cancelled", "delivered"),
}
TERMINAL = {"shipped", "delivered", "cancelled"}

LEAN_CTOR = {
    "pending": ".pending",
    "paid": ".paid",
    "shipped": ".shipped",
    "delivered": ".delivered",
    "cancelled": ".cancelled",
}


def load_impl(path: Path):
    spec = importlib.util.spec_from_file_location("medium_orders_impl", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "transition"):
        raise SystemExit(f"{path} has no transition()")
    return mod.transition


def search(transition):
    for cur in STATUSES:
        for nxt in STATUSES:
            out = transition(cur, nxt)
            if (cur, nxt) in SKIP and out is not None:
                return "no-skip", {"from": cur, "to": nxt, "got": out}
            if (cur, nxt) in BACKWARDS and out is not None:
                return "no-backwards", {"from": cur, "to": nxt, "got": out}
            if cur in TERMINAL and nxt == "cancelled" and out is not None:
                return "cancel-only-open", {"from": cur, "to": nxt, "got": out}
    return None


def write_violation(lean_dir: Path, bullet: str, w: dict) -> Path:
    out = lean_dir / "Scratch" / "Violation.lean"
    out.parent.mkdir(parents=True, exist_ok=True)
    frm = LEAN_CTOR[w["from"]]
    to = LEAN_CTOR[w["to"]]
    if bullet == "no-skip":
        prop = "NoSkip"
        pred = "isSkip"
    elif bullet == "no-backwards":
        prop = "NoBackwards"
        pred = "isBackwards"
    else:
        prop = "CancelOnlyOpen"
        pred = "isClosed"
    body = f"""import MediumOrders.Statements

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `{bullet}` at {w["from"]} → {w["to"]}.
-/
theorem violation_{bullet.replace("-", "_")} :
    ¬ MediumOrders.{prop} MediumOrders.Impl := by
  intro h
  simpa [MediumOrders.Impl, MediumOrders.{pred}] using h {frm} {to} rfl
"""
    out.write_text(body)
    return out


def patch_lean_to_bad(text: str) -> str:
    # Allow pending → shipped, matching fixtures/bad_orders.py
    needle = "| .pending, .paid => some .paid"
    repl = "| .pending, .paid => some .paid\n  | .pending, .shipped => some .shipped"
    if needle not in text:
        return text
    return text.replace(needle, repl, 1)
