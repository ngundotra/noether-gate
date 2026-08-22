import MediumOrders.Statements

/-!
  Named facts about which transitions skip / go backwards / cancel a closed order.
  These do not mention `Impl`, so they survive the deny-path patch.
-/
namespace MediumOrders

@[simp] theorem isSkip_pending_shipped : isSkip .pending .shipped = true := rfl
@[simp] theorem isSkip_pending_delivered : isSkip .pending .delivered = true := rfl
@[simp] theorem isSkip_paid_delivered : isSkip .paid .delivered = true := rfl
@[simp] theorem isSkip_pending_paid : isSkip .pending .paid = false := rfl

@[simp] theorem isBackwards_paid_pending : isBackwards .paid .pending = true := rfl
@[simp] theorem isBackwards_cancelled_paid : isBackwards .cancelled .paid = true := rfl

@[simp] theorem isClosed_shipped_cancelled : isClosed .shipped .cancelled = true := rfl
@[simp] theorem isClosed_delivered_cancelled : isClosed .delivered .cancelled = true := rfl
@[simp] theorem isClosed_pending_cancelled : isClosed .pending .cancelled = false := rfl

end MediumOrders
