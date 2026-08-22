import HardJournal.Statements

/-!
  Per-account / per-kind sums. These are the facts a richer violation
  certificate will want when the witness is longer than one charge.
-/
namespace HardJournal

@[simp] theorem sumRefunds_nil (account : Nat) : sumRefunds account [] = 0 := rfl
@[simp] theorem sumCharges_nil (account : Nat) : sumCharges account [] = 0 := rfl
@[simp] theorem sumRefundsFor_nil (chargeId : Nat) : sumRefundsFor chargeId [] = 0 := rfl

theorem sumRefunds_cons_charge (account : Nat) (e : Entry) (xs : List Entry)
    (h : e.kind = .charge) :
    sumRefunds account (e :: xs) = sumRefunds account xs := by
  simp [sumRefunds, h]

theorem sumCharges_cons_refund (account : Nat) (e : Entry) (xs : List Entry)
    (h : e.kind = .refund) :
    sumCharges account (e :: xs) = sumCharges account xs := by
  simp [sumCharges, h]

theorem sumRefunds_cons_refund_same (account : Nat) (e : Entry) (xs : List Entry)
    (hk : e.kind = .refund) (ha : e.account = account) :
    sumRefunds account (e :: xs) = e.amount + sumRefunds account xs := by
  simp [sumRefunds, hk, ha]

theorem sumCharges_cons_charge_same (account : Nat) (e : Entry) (xs : List Entry)
    (hk : e.kind = .charge) (ha : e.account = account) :
    sumCharges account (e :: xs) = e.amount + sumCharges account xs := by
  simp [sumCharges, hk, ha]

theorem sumRefunds_append (account : Nat) (xs ys : List Entry) :
    sumRefunds account (xs ++ ys) = sumRefunds account xs + sumRefunds account ys := by
  induction xs with
  | nil => simp [sumRefunds]
  | cons e rest ih =>
    simp only [List.cons_append, sumRefunds]
    split <;> simp [ih] <;> omega

theorem sumCharges_append (account : Nat) (xs ys : List Entry) :
    sumCharges account (xs ++ ys) = sumCharges account xs + sumCharges account ys := by
  induction xs with
  | nil => simp [sumCharges]
  | cons e rest ih =>
    simp only [List.cons_append, sumCharges]
    split <;> simp [ih] <;> omega

theorem sumRefundsFor_append (chargeId : Nat) (xs ys : List Entry) :
    sumRefundsFor chargeId (xs ++ ys) =
      sumRefundsFor chargeId xs + sumRefundsFor chargeId ys := by
  induction xs with
  | nil => simp [sumRefundsFor]
  | cons e rest ih =>
    simp only [List.cons_append, sumRefundsFor]
    split <;> simp [ih] <;> omega

theorem sumRefunds_singleton_charge (account amount id : Nat) :
    sumRefunds account [charge account amount id] = 0 := by
  simp [sumRefunds, charge]

theorem sumCharges_singleton_charge (account amount id : Nat) :
    sumCharges account [charge account amount id] = amount := by
  simp [sumCharges, charge]

theorem sumRefunds_charge_then_refund (account chargeAmt refundAmt id : Nat) :
    sumRefunds account [charge account chargeAmt id, refund account refundAmt (id + 1) id] =
      refundAmt := by
  simp [sumRefunds, charge, refund]

theorem sumCharges_charge_then_refund (account chargeAmt refundAmt id : Nat) :
    sumCharges account [charge account chargeAmt id, refund account refundAmt (id + 1) id] =
      chargeAmt := by
  simp [sumCharges, charge, refund]

end HardJournal
