# Contracts

Every pull request must include a Lean contract in `plugin/retellings/`.

That file is the story of the change: what it may do, and what it must never do.

CI checks that the contract is there and that Lean accepts it. A person reads the Lean. That is the review.

## What CI checks

1. The PR actually includes a Lean contract file.
2. Lean accepts the file (it compiles).
3. Nothing is unfinished (`sorry`, `admit`, or an empty proof).
4. The contract does not prove a contradiction (nothing inhabits `False`).

You can say an old rule is broken (`¬ P` or `P → False`). That is a “rules changed” contract. Proving `False` itself is not allowed.

## Where files go

```
plugin/retellings/
  Sample.lean     a contract a person can read
  Sample.md       optional plain-language note
  PR1.lean        example of a “rules changed” contract
  Retellings.lean imports the contracts so Lean can build them
```

Add a new `.lean` file, import it in `Retellings.lean`, and list it in `lakefile.toml` under `roots`.

Run the same checks locally:

```bash
PATH="$HOME/.elan/bin:$PATH" lake build
python3 scripts/check_contract.py
```

## When a contract is not required

A PR that only touches docs, the site, LICENSE, GitHub workflows, or the contract-check itself does not need a new contract. That is so we can land this gate and write about it.

Any PR that changes product or example code must bring a contract.
