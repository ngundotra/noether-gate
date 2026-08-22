# Spec — easy-ledger

Human language. The gate tries to **prove a violation** of these bullets.
If Lean accepts a proof that a bullet fails, the PR is denied.

A transfer moves `amount` from `source` to `dest` on a pair of Nat balances.

| id | Bullet |
|---|---|
| preserves-sum | A transfer must not create or destroy money. Source + dest after a successful transfer equals source + dest before. |
| no-overdraft | If the amount is bigger than the source balance, the transfer is rejected. Nothing changes. |
