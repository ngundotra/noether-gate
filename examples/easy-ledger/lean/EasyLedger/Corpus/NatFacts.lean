import EasyLedger.Statements

/-!
  Tiny Nat facts. Impl-free, so they survive the deny-path patch.
-/
namespace EasyLedger

theorem add_one_ne (n : Nat) : n + 1 ≠ n := by
  omega

theorem not_le_of_lt (a b : Nat) (h : a < b) : ¬ b ≤ a := by
  omega

end EasyLedger
