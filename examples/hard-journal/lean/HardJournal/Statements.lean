/-!
  Statements for hard-journal.

  `Impl` is the Lean model of `src/journal.py`. Keep them in lockstep.
  This file is *statements only*. Safety proofs live in `Safe.lean`.
  Helper lemmas live in `HardJournal/Corpus/` — grow them with `scripts/corpus.py`.
-/
namespace HardJournal

inductive Kind where
  | charge
  | refund
  deriving DecidableEq, Repr

structure Entry where
  kind : Kind
  account : Nat
  amount : Nat
  id : Nat
  chargeId : Nat
  deriving DecidableEq, Repr

@[simp] def charge (account amount id : Nat) : Entry :=
  { kind := .charge, account, amount, id, chargeId := 0 }

@[simp] def refund (account amount id chargeId : Nat) : Entry :=
  { kind := .refund, account, amount, id, chargeId }

def findCharge (id : Nat) : List Entry → Option Entry
  | [] => none
  | e :: rest =>
    if e.kind == .charge && e.id == id then some e
    else findCharge id rest

def sumRefundsFor (chargeId : Nat) : List Entry → Nat
  | [] => 0
  | e :: rest =>
    let recSum := sumRefundsFor chargeId rest
    if e.kind == .refund && e.chargeId == chargeId then e.amount + recSum else recSum

def sumRefunds (account : Nat) : List Entry → Nat
  | [] => 0
  | e :: rest =>
    let recSum := sumRefunds account rest
    if e.kind == .refund && e.account == account then e.amount + recSum else recSum

def sumCharges (account : Nat) : List Entry → Nat
  | [] => 0
  | e :: rest =>
    let recSum := sumCharges account rest
    if e.kind == .charge && e.account == account then e.amount + recSum else recSum

def sumAmounts : List Entry → Nat
  | [] => 0
  | e :: rest => e.amount + sumAmounts rest

/-- Model of `src/journal.py`. -/
def Impl (journal : List Entry) (entry : Entry) : Option (List Entry) :=
  match entry.kind with
  | .charge =>
    if entry.amount = 0 then none else some (journal ++ [entry])
  | .refund =>
    match findCharge entry.chargeId journal with
    | none => none
    | some c =>
      if c.account ≠ entry.account then none
      else
        let prior := sumRefundsFor entry.chargeId journal
        if prior + entry.amount > c.amount then none
        else some (journal ++ [entry])

/-- Bullet `refunds-reference-charge`.
    A refund against a journal that has no matching charge is rejected. -/
def RefundsReferenceCharge (f : List Entry → Entry → Option (List Entry)) : Prop :=
  ∀ (journal : List Entry) (entry : Entry),
    entry.kind = .refund →
    findCharge entry.chargeId journal = none →
    f journal entry = none

/-- Bullet `refunds-bounded`.
    One charge, then a refund on that charge: the result (if any) stays bounded.
    The general list-sum facts needed to scale this live in `Corpus/`. -/
def RefundsBounded (f : List Entry → Entry → Option (List Entry)) : Prop :=
  ∀ (account chargeAmt refundAmt id : Nat),
    match f [charge account chargeAmt id] (refund account refundAmt (id + 1) id) with
    | none => True
    | some out => sumRefunds account out ≤ sumCharges account out

end HardJournal
