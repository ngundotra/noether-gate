import MediumOrders.Statements

/-!
  Optional proofs that the current model satisfies the bullets.
  Not a default Lake target.
-/
namespace MediumOrders

theorem impl_no_skip : NoSkip Impl := by
  intro frm to h
  cases frm <;> cases to <;> simp [isSkip] at h <;> simp [Impl]

theorem impl_no_backwards : NoBackwards Impl := by
  intro frm to h
  cases frm <;> cases to <;> simp [isBackwards] at h <;> simp [Impl]

theorem impl_cancel_only_open : CancelOnlyOpen Impl := by
  intro frm to h
  cases frm <;> cases to <;> simp [isClosed] at h <;> simp [Impl]

end MediumOrders
