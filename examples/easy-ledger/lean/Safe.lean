import EasyLedger.Statements
import EasyLedger.Corpus

/-!
  Optional proofs that the current model satisfies the bullets.
  Not a default Lake target, so a bad PR can still produce a violation certificate.
-/
namespace EasyLedger

theorem impl_preserves_sum : PreservesSum Impl := by
  intro source dest amount
  unfold Impl
  split <;> simp_all
  omega

theorem impl_no_overdraft : NoOverdraft Impl := by
  intro source dest amount h
  unfold Impl
  simp [h]

end EasyLedger
