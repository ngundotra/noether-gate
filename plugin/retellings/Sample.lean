/-!
  A sample contract: a transfer moves `amount` once and does not mint money.

  This is the shape of a contract a person can read. It is not a claim
  about any Python in this repo.
-/
namespace Sample

/-- One-shot send: take `amount` from source, give it to dest. -/
def transfer (source dest amount : Nat) : Option (Nat × Nat) :=
  if amount ≤ source then
    some (source - amount, dest + amount)
  else
    none

/-- Do not create or destroy money. -/
def PreservesSum (f : Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount,
    match f source dest amount with
    | none => True
    | some (s', d') => s' + d' = source + dest

/-- A successful send moves `amount` once. -/
def MovesAmountOnce (f : Nat → Nat → Nat → Option (Nat × Nat)) : Prop :=
  ∀ source dest amount,
    match f source dest amount with
    | none => True
    | some (s', d') => s' + amount = source ∧ d' = dest + amount

/-- Start 10 and 10, send 5: the pair is (5, 15). -/
theorem send_ten_and_ten : transfer 10 10 5 = some (5, 15) := rfl

/-- That same send keeps the sum. -/
theorem send_preserves_this_sum : 5 + 15 = 10 + 10 := rfl

theorem transfer_preserves_sum : PreservesSum transfer := by
  intro source dest amount
  by_cases h : amount ≤ source
  · simp [transfer, h]
    omega
  · simp [transfer, h]

theorem transfer_moves_once : MovesAmountOnce transfer := by
  intro source dest amount
  by_cases h : amount ≤ source
  · simp [transfer, h]
    try omega
  · simp [transfer, h]

end Sample
