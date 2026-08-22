import HardJournal.Statements
import HardJournal.Corpus

/-!
  Optional proofs that the current model satisfies the bullets.
  Not a default Lake target.
-/
namespace HardJournal

theorem impl_refunds_reference : RefundsReferenceCharge Impl := by
  intro journal entry hk hfind
  cases entry with
  | mk kind account amount id chargeId =>
    cases kind with
    | charge => cases hk
    | refund =>
      simp [Impl, hfind]

theorem impl_eval (account chargeAmt refundAmt id : Nat) :
    Impl [charge account chargeAmt id] (refund account refundAmt (id + 1) id) =
      if chargeAmt < refundAmt then none
      else some [charge account chargeAmt id, refund account refundAmt (id + 1) id] := by
  simp [Impl, charge, refund, findCharge, sumRefundsFor]

theorem impl_refunds_bounded : RefundsBounded Impl := by
  intro account chargeAmt refundAmt id
  rw [impl_eval]
  by_cases h : chargeAmt < refundAmt
  · simp [h]
  · simp [h, sumRefunds, sumCharges, charge, refund]
    omega

theorem impl_refund_missing (journal : List Entry) (entry : Entry)
    (hk : entry.kind = .refund)
    (hfind : findCharge entry.chargeId journal = none) :
    Impl journal entry = none := by
  simp [Impl, hk, hfind]

theorem impl_charge_zero (journal : List Entry) (entry : Entry)
    (hk : entry.kind = .charge) (hz : entry.amount = 0) :
    Impl journal entry = none := by
  simp [Impl, hk, hz]

end HardJournal
