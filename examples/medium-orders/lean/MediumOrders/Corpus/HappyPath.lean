import MediumOrders.Statements

/-!
  The happy path is a chain. Agents can add more transition lemmas here.
-/
namespace MediumOrders

@[simp] theorem pending_to_paid : Impl .pending .paid = some .paid := rfl
@[simp] theorem paid_to_shipped : Impl .paid .shipped = some .shipped := rfl
@[simp] theorem shipped_to_delivered : Impl .shipped .delivered = some .delivered := rfl

theorem skip_pending_shipped : isSkip .pending .shipped = true := rfl
theorem skip_pending_delivered : isSkip .pending .delivered = true := rfl
theorem skip_paid_delivered : isSkip .paid .delivered = true := rfl

end MediumOrders
