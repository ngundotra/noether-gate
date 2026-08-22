/-!
  Corpus for the ledger example.

  `Impl` is the Lean model of `example/ledger.py`.
  Keep them in lockstep. The gate searches for a witness that `Impl`
  violates a bullet, then asks Lean to certify that witness.

  This file is *statements only*. Proofs that Impl is safe live in
  `Noether/Safe.lean` and are not part of the deny path.
-/
namespace Noether.Ledger

/-- Model of `example/ledger.py`. -/
def Impl (source dest amount : Nat) : Option (Nat × Nat) :=
  if amount ≤ source then
    some (source - amount, dest + amount)
  else
    none

/-- Bullet `preserves-sum`. -/
def PreservesSum (f : Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount,
    match f source dest amount with
    | none => True
    | some (s', d') => s' + d' = source + dest

/-- Bullet `no-overdraft`. -/
def NoOverdraft (f : Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount, source < amount → f source dest amount = none

end Noether.Ledger
