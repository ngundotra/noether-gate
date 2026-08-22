import HardJournal.Statements

/-!
  Facts about `Impl` on refunds. The gate's Python search finds a witness;
  these lemmas are what a longer certificate would cite.
-/
namespace HardJournal

theorem impl_refund_missing (journal : List Entry) (entry : Entry)
    (hk : entry.kind = .refund)
    (hfind : findCharge entry.chargeId journal = none) :
    Impl journal entry = none := by
  simp [Impl, hk, hfind]

theorem impl_charge_zero (journal : List Entry) (entry : Entry)
    (hk : entry.kind = .charge) (hz : entry.amount = 0) :
    Impl journal entry = none := by
  simp [Impl, hk, hz]

theorem impl_refund_over (journal : List Entry) (entry c : Entry)
    (hk : entry.kind = .refund)
    (hfind : findCharge entry.chargeId journal = some c)
    (ha : c.account = entry.account)
    (hover : c.amount < sumRefundsFor entry.chargeId journal + entry.amount) :
    Impl journal entry = none := by
  simp [Impl, hk, hfind, ha, hover]

end HardJournal
