/-!
  Retelling of https://github.com/ngundotra/noether-gate/pull/1

  The send now takes a retry count. Each retry sends `amount` again
  if the source still has enough.
-/
namespace PR1

/-- One more send of `amount`, or no-op if the source cannot pay. -/
def retryOnce (src dst amount : Nat) : Nat × Nat :=
  if amount ≤ src then (src - amount, dst + amount) else (src, dst)

/-- Extra sends after the first one already happened. -/
def applyRetries (src dst amount : Nat) : Nat → Nat × Nat
  | 0 => (src, dst)
  | n + 1 =>
    let p := retryOnce src dst amount
    applyRetries p.1 p.2 amount n

/-- Model of `transfer` after the PR. -/
def transfer (source dest amount retries : Nat) : Option (Nat × Nat) :=
  if amount ≤ source then
    some (applyRetries (source - amount) (dest + amount) amount retries)
  else
    none

/-- Do not create or destroy money. -/
def PreservesSum (f : Nat → Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount retries s' d',
    f source dest amount retries = some (s', d') → s' + d' = source + dest

/-- Reject an overdraft. Nothing changes. -/
def NoOverdraft (f : Nat → Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount retries, source < amount → f source dest amount retries = none

/-- Old one-shot rule: a transfer moves `amount` once. -/
def MovesAmount (f : Nat → Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount retries,
    match f source dest amount retries with
    | none => True
    | some (s', d') => s' + amount = source ∧ d' = dest + amount

theorem retryOnce_sum (src dst amount : Nat) :
    (retryOnce src dst amount).1 + (retryOnce src dst amount).2 = src + dst := by
  by_cases h : amount ≤ src
  · simp [retryOnce, h]; omega
  · simp [retryOnce, h]

theorem applyRetries_sum (src dst amount n : Nat) :
    (applyRetries src dst amount n).1 + (applyRetries src dst amount n).2 = src + dst := by
  induction n generalizing src dst with
  | zero => simp [applyRetries]
  | succ n ih =>
    simp [applyRetries]
    exact (ih _ _).trans (retryOnce_sum src dst amount)

theorem transfer_preserves_sum : PreservesSum transfer := by
  intro source dest amount retries s' d' ht
  by_cases h : amount ≤ source
  · simp [transfer, h] at ht
    have hsum := applyRetries_sum (source - amount) (dest + amount) amount retries
    rw [ht] at hsum
    have hcancel : (source - amount) + (dest + amount) = source + dest := by omega
    exact hsum.trans hcancel
  · simp [transfer, h] at ht

theorem transfer_no_overdraft : NoOverdraft transfer := by
  intro source dest amount retries hlt
  have : ¬ amount ≤ source := Nat.not_le_of_gt hlt
  simp [transfer, this]

theorem send_once : transfer 10 10 5 0 = some (5, 15) := rfl

theorem send_with_retry : transfer 10 10 5 1 = some (0, 20) := rfl

/-- Start 10 and 10, send 5 with one retry: not the one-shot pair. -/
theorem totals_no_longer_match : transfer 10 10 5 1 ≠ transfer 10 10 5 0 := by
  simp [send_with_retry, send_once]

/-- The old “moves `amount` once” rule is false after this PR. -/
theorem not_moves_amount : ¬ MovesAmount transfer := by
  intro h
  simpa [transfer, applyRetries, retryOnce] using h 10 10 5 1

end PR1
