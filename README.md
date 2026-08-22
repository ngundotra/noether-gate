# Noether Gate

CI that takes human-language bullets and tries to **prove they are violated**.

If Lean accepts a proof of a violation, the PR is denied.
If no violation is proved, the check stays green. That is not a proof of correctness.
It is "we could not certify a bug."

This repo is an experimental scratch space: three examples (easy / medium / hard)
plus a tiny corpus tool so agents can grow helper lemmas per example.

## Examples

| name | idea | bullets |
|---|---|---|
| `easy-ledger` | Nat transfer | `preserves-sum`, `no-overdraft` |
| `medium-orders` | order state machine | `no-skip`, `no-backwards`, `cancel-only-open` |
| `hard-journal` | charges + refunds | `refunds-reference-charge`, `refunds-bounded` |

Each example is self-contained:

```
examples/<name>/
  SPEC.md              human bullets
  src/                 tiny product
  fixtures/bad_*       should deny
  lean/                statements + Corpus/ lemmas + optional Safe.lean
  search.py            witness search + Lean certificate writer
```

`--use-bad-fixture` runs every pair in `search.py`'s `bad_cases()` (falls back to one `BAD_IMPL`).

| example | fixture | what it does | bullet that should deny |
|---|---|---|---|
| `easy-ledger` | `fixtures/bad_ledger.py` | mints `+1` on dest | `preserves-sum` |
| `easy-ledger` | `fixtures/bad_overdraft.py` | accepts an overdraft as a no-op | `no-overdraft` |
| `medium-orders` | `fixtures/bad_orders.py` | `pending → shipped` | `no-skip` |
| `medium-orders` | `fixtures/bad_backwards.py` | `paid → pending` | `no-backwards` |
| `medium-orders` | `fixtures/bad_cancel_closed.py` | `shipped → cancelled` | `cancel-only-open` |
| `hard-journal` | `fixtures/bad_journal.py` | refund bigger than its charge | `refunds-bounded` |
| `hard-journal` | `fixtures/bad_orphan_refund.py` | refund with no matching charge | `refunds-reference-charge` |

## Run the gate

Lean 4.24.0 via elan (`PATH=$HOME/.elan/bin:$PATH`).

```bash
python3 scripts/gate.py --example easy-ledger
python3 scripts/gate.py --example medium-orders
python3 scripts/gate.py --example hard-journal
python3 scripts/gate.py --all
```

Bad fixtures (exit 0 only if Lean accepts a violation certificate):

```bash
python3 scripts/gate.py --example easy-ledger --use-bad-fixture --expect-deny
python3 scripts/gate.py --example medium-orders --use-bad-fixture --expect-deny
python3 scripts/gate.py --example hard-journal --use-bad-fixture --expect-deny
```

## Grow the corpus

```bash
python3 scripts/corpus.py list --example hard-journal
python3 scripts/corpus.py add-lemma --example hard-journal --name filter_sum_le
```

`add-lemma` writes a stub under that example's `lean/<Pkg>/Corpus/` and prints the import.

## Agent loop

See `AGENTS.md`. Short version: read `SPEC.md` + `src/`, search for a violation,
add a helper lemma via the corpus tool if the certificate needs it, retry.
Do not write essays.

## What a deny looks like

On each run, `scripts/gate.py`:

1. Searches a small input grid in Python for a witness.
2. If it finds one, writes `lean/Scratch/Violation.lean` — a theorem `¬ Property Impl`.
3. Runs `lake env lean` on that file. If the kernel accepts it, exit 1 (deny).

Statements live in the default library. Optional safety proofs are in `Safe.lean`
and are **not** part of the default target, so a bad fixture can mutate `Impl`
without breaking `impl_satisfies` theorems.

## Sandbox

```bash
docker build -t noether-gate .
docker run --rm -v "$PWD":/src noether-gate
```
