"""Witness search + Lean certificate for hard-journal."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PKG = "HardJournal"
STATEMENTS = "HardJournal/Statements.lean"
DEFAULT_IMPL = "src/journal.py"
BAD_IMPL = "fixtures/bad_journal.py"


def load_impl(path: Path):
    spec = importlib.util.spec_from_file_location("hard_journal_impl", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "apply") or not hasattr(mod, "Entry"):
        raise SystemExit(f"{path} needs apply() and Entry")
    return mod


def _entry(mod, kind, account, amount, id_, charge_id=0):
    return mod.Entry(kind=kind, account=account, amount=amount, id=id_, charge_id=charge_id)


def search(mod):
    apply = mod.apply
    # refunds-reference-charge: refund with a missing charge id
    for acct in range(0, 3):
        for amt in range(1, 5):
            for cid in range(0, 4):
                e = _entry(mod, "refund", acct, amt, 99, cid)
                out = apply([], e)
                if out is not None:
                    return "refunds-reference-charge", {
                        "account": acct,
                        "amount": amt,
                        "charge_id": cid,
                    }

    # refunds-bounded: one charge, then a refund that overdraws it
    for acct in range(0, 3):
        for charge_amt in range(1, 6):
            for refund_amt in range(0, 7):
                for cid in (1, 2):
                    charge = _entry(mod, "charge", acct, charge_amt, cid, 0)
                    j1 = apply([], charge)
                    if j1 is None:
                        continue
                    refund = _entry(mod, "refund", acct, refund_amt, cid + 10, cid)
                    out = apply(j1, refund)
                    if refund_amt > charge_amt:
                        if out is not None:
                            return "refunds-bounded", {
                                "account": acct,
                                "charge_amt": charge_amt,
                                "refund_amt": refund_amt,
                                "id": cid,
                            }
                    elif out is None and refund_amt > 0:
                        # good impl should accept a within-bound refund; not a deny bullet
                        # but if it rejects a legal refund we ignore it here
                        pass
                    elif out is not None:
                        r = sum(e.amount for e in out if e.account == acct and e.kind == "refund")
                        c = sum(e.amount for e in out if e.account == acct and e.kind == "charge")
                        if r > c:
                            return "refunds-bounded", {
                                "account": acct,
                                "charge_amt": charge_amt,
                                "refund_amt": refund_amt,
                                "id": cid,
                            }
    return None


def write_violation(lean_dir: Path, bullet: str, w: dict) -> Path:
    out = lean_dir / "Scratch" / "Violation.lean"
    out.parent.mkdir(parents=True, exist_ok=True)
    if bullet == "refunds-reference-charge":
        acct, amt, cid = w["account"], w["amount"], w["charge_id"]
        body = f"""import HardJournal.Statements

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `refunds-reference-charge` at account={acct} amount={amt} chargeId={cid}.
-/
theorem violation_refunds_reference_charge :
    ¬ HardJournal.RefundsReferenceCharge HardJournal.Impl := by
  intro h
  simpa [HardJournal.Impl, HardJournal.findCharge] using
    h [] (HardJournal.refund {acct} {amt} 99 {cid}) rfl rfl
"""
    else:
        acct = w["account"]
        camt = w["charge_amt"]
        ramt = w["refund_amt"]
        id_ = w["id"]
        body = f"""import HardJournal.Statements

/-!
  Auto-generated certificate. If this file typechecks, the PR violates
  bullet `refunds-bounded` at account={acct} charge={camt} refund={ramt} id={id_}.
-/
theorem violation_refunds_bounded :
    ¬ HardJournal.RefundsBounded HardJournal.Impl := by
  intro h
  simpa [HardJournal.Impl, HardJournal.charge, HardJournal.refund,
         HardJournal.findCharge, HardJournal.sumRefundsFor,
         HardJournal.sumRefunds, HardJournal.sumCharges] using
    h {acct} {camt} {ramt} {id_}
"""
    out.write_text(body)
    return out


def patch_lean_to_bad(text: str) -> str:
    # Drop the remaining-balance guard so a refund may exceed its charge.
    old = """        let prior := sumRefundsFor entry.chargeId journal
        if prior + entry.amount > c.amount then none
        else some (journal ++ [entry])"""
    new = """        let _prior := sumRefundsFor entry.chargeId journal
        some (journal ++ [entry])"""
    if old not in text:
        return text
    return text.replace(old, new, 1)
