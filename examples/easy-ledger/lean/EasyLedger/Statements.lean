/-!
  Statements for easy-ledger.

  `Impl` is the Lean model of `src/ledger.py`. Keep them in lockstep.
  This file is *statements only*. Proofs that Impl is safe live in
  `Safe.lean` and are not part of the default library.
-/
namespace EasyLedger

/-- Model of `src/ledger.py`. -/
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

end EasyLedger
