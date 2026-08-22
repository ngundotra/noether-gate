# Noether Gate

CI that takes human-language bullets and tries to **prove they are violated** on every PR.

If Lean accepts a proof of a violation, the PR is denied.
If no violation is proved, the check stays green. That is not a proof of correctness. It is "we could not certify a bug."

## Why this shape

Agents write more code than anyone can review. The useful CI question is not "did an agent write a correctness proof?" (hard, often `sorry`). It is "can an agent, in a Lean sandbox, produce a short proof that this PR breaks a named bullet?"

That is Lean golf aimed at the diff: search for a small violation certificate, kernel-check it, deny on success.

## First example

`SPEC.md` has two bullets about a tiny ledger.

| id | Bullet |
|---|---|
| preserves-sum | A transfer must not create or destroy money |
| no-overdraft | Overdrafts are rejected |

`example/ledger.py` is the product. `lean/Noether/Ledger.lean` is the corpus: a Lean model of that function plus the two properties.

On each run, `scripts/gate.py`:

1. Searches a small input grid in Python for a witness.
2. If it finds one, writes `lean/Scratch/Violation.lean` — a theorem `¬ Property Impl` at that witness.
3. Runs `lake build`. If the kernel accepts the theorem, exit 1 (deny).

The bad fixture `fixtures/bad_ledger.py` mints one extra coin. CI has a job that expects that path to deny.

## Sandbox

`Dockerfile` is a Lean 4.24 image with Python. Locally:

```bash
docker build -t noether-gate .
docker run --rm -v "$PWD":/src noether-gate
```

Or without Docker, if you have [elan](https://github.com/leanprover/elan):

```bash
python3 scripts/gate.py
python3 scripts/gate.py --impl fixtures/bad_ledger.py --expect-deny
```

## What we are trying to learn

| Question | This experiment |
|---|---|
| Can Lean be the deny-certificate, not the whole correctness proof? | Yes, that is the point |
| Can we start from English bullets? | The bullets live in `SPEC.md`. The Lean props are maintained by hand in v0 |
| Will the Lean model drift from the code? | Almost certainly. The gate already fails closed if Python sees a bug the model cannot certify |
| Do we need a real LLM agent yet? | Not for this example. The search is exhaustive and tiny. Next step is an agent that golfs harder violations and keeps the model in sync |

## Status

First example. Play with it. If this is the wrong way to use Lean, that is the finding.
