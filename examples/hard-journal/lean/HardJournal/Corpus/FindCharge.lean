import HardJournal.Statements

/-!
  Looking up a charge by id.
-/
namespace HardJournal

@[simp] theorem findCharge_nil (id : Nat) : findCharge id [] = none := rfl

theorem findCharge_cons_hit (id : Nat) (e : Entry) (xs : List Entry)
    (hk : e.kind = .charge) (hi : e.id = id) :
    findCharge id (e :: xs) = some e := by
  simp [findCharge, hk, hi]

theorem findCharge_cons_miss (id : Nat) (e : Entry) (xs : List Entry)
    (h : e.kind ≠ .charge ∨ e.id ≠ id) :
    findCharge id (e :: xs) = findCharge id xs := by
  simp [findCharge]
  cases h with
  | inl hk => simp [hk]
  | inr hi => simp [hi]

theorem findCharge_singleton_charge (account amount id : Nat) :
    findCharge id [charge account amount id] = some (charge account amount id) := by
  simp [findCharge, charge]

end HardJournal
