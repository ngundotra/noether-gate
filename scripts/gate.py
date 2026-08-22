#!/usr/bin/env python3
"""Search for a spec violation, certify it in Lean, deny if Lean accepts the proof."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean"
DEFAULT_IMPL = ROOT / "example" / "ledger.py"


def load_transfer(path: Path):
    spec = importlib.util.spec_from_file_location("ledger", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "transfer"):
        raise SystemExit(f"{path} has no transfer()")
    return mod.transfer


def search(transfer):
    """Tiny exhaustive search. Returns (bullet_id, witness) or None."""
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


def write_violation_lean(bullet: str, w: dict) -> Path:
    out = LEAN_DIR / "Scratch" / "Violation.lean"
    out.parent.mkdir(parents=True, exist_ok=True)
    s, d, a = w["source"], w["dest"], w["amount"]
    if bullet == "preserves-sum":
        body = f"""import Noether.Ledger

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `preserves-sum` at source={s} dest={d} amount={a}.
-/
theorem violation_preserves_sum : ¬ Noether.Ledger.PreservesSum Noether.Ledger.Impl := by
  intro h
  simpa [Noether.Ledger.Impl] using h {s} {d} {a}
"""
    else:
        body = f"""import Noether.Ledger

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `no-overdraft` at source={s} dest={d} amount={a}.
-/
theorem violation_no_overdraft : ¬ Noether.Ledger.NoOverdraft Noether.Ledger.Impl := by
  intro h
  have := h {s} {d} {a} (by omega)
  simpa [Noether.Ledger.Impl] using this
"""
    out.write_text(body)
    return out


def lake_build(extra: Path | None = None) -> int:
    rc = subprocess.call(["lake", "build"], cwd=LEAN_DIR)
    if rc != 0 or extra is None:
        return rc
    return subprocess.call(["lake", "env", "lean", str(extra.relative_to(LEAN_DIR))], cwd=LEAN_DIR)


def main() -> int:
    p = argparse.ArgumentParser(description="Noether Gate")
    p.add_argument("--impl", type=Path, default=DEFAULT_IMPL)
    p.add_argument(
        "--expect-deny",
        action="store_true",
        help="Exit 0 only if a violation is proved (used by the bad-fixture job).",
    )
    args = p.parse_args()

    transfer = load_transfer(args.impl)
    found = search(transfer)

    scratch = LEAN_DIR / "Scratch" / "Violation.lean"
    if scratch.exists():
        scratch.unlink()

    if found is None:
        print("Noether Gate: no witness in the small search. Building corpus.")
        rc = lake_build()
        if rc != 0:
            print("Noether Gate: corpus failed to build.")
            return rc
        if args.expect_deny:
            print("Noether Gate: expected a deny, found none.")
            return 1
        print("Noether Gate: no violation proved. Approve.")
        return 0

    bullet, witness = found
    print(f"Noether Gate: Python found a witness for `{bullet}`: {witness}")
    print("Writing a Lean certificate and asking the kernel to accept it.")
    path = write_violation_lean(bullet, witness)
    rc = lake_build(path)
    if rc == 0:
        print("Noether Gate: Lean accepted the violation proof. Deny.")
        return 0 if args.expect_deny else 1
    print("Noether Gate: witness found in Python but Lean rejected the certificate.")
    print("That usually means the Lean model is out of sync with the implementation.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
