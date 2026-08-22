"""Witness search + Lean certificate for easy-ledger."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PKG = "EasyLedger"
STATEMENTS = "EasyLedger/Statements.lean"
DEFAULT_IMPL = "src/ledger.py"
BAD_IMPL = "fixtures/bad_ledger.py"


def load_impl(path: Path):
    spec = importlib.util.spec_from_file_location("easy_ledger_impl", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "transfer"):
        raise SystemExit(f"{path} has no transfer()")
    return mod.transfer


def search(transfer):
    for source in range(0, 8):
        for dest in range(0, 8):
            for amount in range(0, 8):
                out = transfer(source, dest, amount)
                if amount > source:
                    if out is not None:
                        return "no-overdraft", {
                            "source": source,
                            "dest": dest,
                            "amount": amount,
                            "kind": "expected_none",
                        }
                    continue
                if out is None:
                    return "no-overdraft", {
                        "source": source,
                        "dest": dest,
                        "amount": amount,
                        "kind": "unexpected_none",
                    }
                s2, d2 = out
                if s2 + d2 != source + dest:
                    return "preserves-sum", {
                        "source": source,
                        "dest": dest,
                        "amount": amount,
                        "got": (s2, d2),
                        "kind": "sum",
                    }
    return None


def write_violation(lean_dir: Path, bullet: str, w: dict) -> Path:
    out = lean_dir / "Scratch" / "Violation.lean"
    out.parent.mkdir(parents=True, exist_ok=True)
    s, d, a = w["source"], w["dest"], w["amount"]
    if bullet == "preserves-sum":
        body = f"""import EasyLedger.Statements

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `preserves-sum` at source={s} dest={d} amount={a}.
-/
theorem violation_preserves_sum : ¬ EasyLedger.PreservesSum EasyLedger.Impl := by
  intro h
  simpa [EasyLedger.Impl] using h {s} {d} {a}
"""
    else:
        body = f"""import EasyLedger.Statements

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `no-overdraft` at source={s} dest={d} amount={a}.
-/
theorem violation_no_overdraft : ¬ EasyLedger.NoOverdraft EasyLedger.Impl := by
  intro h
  simpa [EasyLedger.Impl] using h {s} {d} {a} (by omega)
"""
    out.write_text(body)
    return out


def patch_lean_to_bad(text: str) -> str:
    return text.replace("dest + amount)", "dest + amount + 1)", 1)
