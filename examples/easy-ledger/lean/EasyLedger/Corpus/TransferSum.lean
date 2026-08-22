import EasyLedger.Statements

/-!
  Helper: subtracting from the source and adding to the dest cancels.
  Agents can grow more facts next to this one.
-/
namespace EasyLedger

@[simp] theorem sub_add_cancel (source dest amount : Nat) (h : amount ≤ source) :
    (source - amount) + (dest + amount) = source + dest := by
  omega

end EasyLedger
