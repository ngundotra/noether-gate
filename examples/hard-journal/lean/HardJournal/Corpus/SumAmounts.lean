import HardJournal.Statements

/-!
  List-sum lemmas. Agents: add more next to these, do not rewrite them in place
  unless you are fixing a compile error.
-/
namespace HardJournal

@[simp] theorem sumAmounts_nil : sumAmounts [] = 0 := rfl

@[simp] theorem sumAmounts_cons (e : Entry) (xs : List Entry) :
    sumAmounts (e :: xs) = e.amount + sumAmounts xs := rfl

theorem sumAmounts_append (xs ys : List Entry) :
    sumAmounts (xs ++ ys) = sumAmounts xs + sumAmounts ys := by
  induction xs with
  | nil => simp [sumAmounts]
  | cons e rest ih =>
    simp [sumAmounts, ih]
    omega

@[simp] theorem sumAmounts_singleton (e : Entry) : sumAmounts [e] = e.amount := rfl

end HardJournal
