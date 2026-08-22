/-!
  # Send with retries

  This file is the contract. If you cannot agree with it, stop.

  You are agreeing to three rules:

  1. A send never creates or destroys money.
  2. A send never takes more than the source has.
  3. If you ask for retries, each retry pays the same amount again
     from the source, only while the source still has enough.

  Concrete check, so we mean the same numbers:

  * start 10 and 10, send 5 once            →  5 and 15
  * start 10 and 10, send 5 with one retry  →  0 and 20
-/

namespace Send

/-- Two balances: who pays, and who receives. -/
structure Pair where
  source : Nat
  dest : Nat

/-- Pay `amount` once. Refuse if the source cannot cover it. -/
def payOnce (p : Pair) (amount : Nat) : Option Pair :=
  if amount ≤ p.source then
    some { source := p.source - amount, dest := p.dest + amount }
  else
    none

/--
  Pay once, then pay that same amount again `retries` times.
  A retry that the source cannot cover is skipped. The first pay
  still has to succeed, or the whole send is refused.
-/
def send (p : Pair) (amount : Nat) : Nat → Option Pair
  | 0 => payOnce p amount
  | n + 1 =>
    match send p amount n with
    | none => none
    | some mid =>
      match payOnce mid amount with
      | none => some mid
      | some done => some done

/-! ## The numbers a person can check -/

/-- Start 10 and 10. Send 5. You get 5 and 15. -/
theorem start_10_10_send_5 :
    send { source := 10, dest := 10 } 5 0 =
      some { source := 5, dest := 15 } := rfl

/-- Same start. Send 5 with one retry. You get 0 and 20. -/
theorem start_10_10_send_5_with_one_retry :
    send { source := 10, dest := 10 } 5 1 =
      some { source := 0, dest := 20 } := rfl

/-! ## The rules you are signing -/

theorem payOnce_keeps_the_sum
    (p : Pair) (amount : Nat) (q : Pair)
    (ok : payOnce p amount = some q) :
    q.source + q.dest = p.source + p.dest := by
  unfold payOnce at ok
  split at ok
  · next _ =>
    injection ok with h
    subst h
    simp
    omega
  · cases ok

/-- After a successful send, the two sides still add up. -/
theorem never_creates_money
    (start : Pair) (amount retries : Nat) (finish : Pair)
    (ok : send start amount retries = some finish) :
    finish.source + finish.dest = start.source + start.dest := by
  induction retries generalizing finish with
  | zero =>
    exact payOnce_keeps_the_sum start amount finish (by simpa [send] using ok)
  | succ n ih =>
    cases hMid : send start amount n with
    | none => simp [send, hMid] at ok
    | some mid =>
      cases hPay : payOnce mid amount with
      | none =>
        simp [send, hMid, hPay] at ok
        subst ok
        exact ih mid hMid
      | some done =>
        simp [send, hMid, hPay] at ok
        subst ok
        have hMidSum := ih mid hMid
        have hPaySum := payOnce_keeps_the_sum mid amount done hPay
        omega

/-- If the source cannot cover the first amount, the send is refused. -/
theorem never_accepts_an_overdraft
    (start : Pair) (amount retries : Nat)
    (too_big : start.source < amount) :
    send start amount retries = none := by
  have hnot : ¬ amount ≤ start.source := Nat.not_le_of_gt too_big
  induction retries with
  | zero => simp [send, payOnce, hnot]
  | succ n ih => simp [send, ih]

end Send
