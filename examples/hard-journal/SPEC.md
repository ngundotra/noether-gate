# Spec — hard-journal

A journal is a list of charges and refunds. Each refund points at a charge.

| id | Bullet |
|---|---|
| refunds-reference-charge | A refund is rejected unless it names an existing charge on the same account. |
| refunds-bounded | After a successful apply, `sum(refunds) ≤ sum(charges)` for the account. A refund must not exceed the remaining amount on the charge it names. |

The Lean corpus has list-sum / filter / find lemmas. Grow them with `scripts/corpus.py` when a certificate needs a new fact.
