/-!
  Statements for medium-orders.

  `Impl` is the Lean model of `src/orders.py`. Keep them in lockstep.
  This file is *statements only*. Safety proofs live in `Safe.lean`.
-/
namespace MediumOrders

inductive Status where
  | pending
  | paid
  | shipped
  | delivered
  | cancelled
  deriving DecidableEq, Repr

/-- Model of `src/orders.py`. -/
def Impl : Status → Status → Option Status
  | .pending, .paid => some .paid
  | .paid, .shipped => some .shipped
  | .shipped, .delivered => some .delivered
  | .pending, .cancelled => some .cancelled
  | .paid, .cancelled => some .cancelled
  | _, _ => none

/-- Steps that skip a required state. -/
def isSkip : Status → Status → Bool
  | .pending, .shipped | .pending, .delivered | .paid, .delivered => true
  | _, _ => false

/-- Backwards or out-of-cancelled moves. -/
def isBackwards : Status → Status → Bool
  | .paid, .pending
  | .shipped, .pending | .shipped, .paid
  | .delivered, .pending | .delivered, .paid | .delivered, .shipped
  | .cancelled, .pending | .cancelled, .paid | .cancelled, .shipped
  | .cancelled, .delivered => true
  | _, _ => false

/-- Statuses that may not move to cancelled. -/
def isClosed : Status → Status → Bool
  | .shipped, .cancelled | .delivered, .cancelled | .cancelled, .cancelled => true
  | _, _ => false

/-- Bullet `no-skip`. -/
def NoSkip (f : Status → Status → Option Status) : Prop :=
  ∀ frm to, isSkip frm to = true → f frm to = none

/-- Bullet `no-backwards`. -/
def NoBackwards (f : Status → Status → Option Status) : Prop :=
  ∀ frm to, isBackwards frm to = true → f frm to = none

/-- Bullet `cancel-only-open`. -/
def CancelOnlyOpen (f : Status → Status → Option Status) : Prop :=
  ∀ frm to, isClosed frm to = true → f frm to = none

end MediumOrders
