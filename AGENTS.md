# Agent instructions

You are in a sandbox whose job is: **certify a spec violation, or report that you could not.**

Do not write essays. Do not open other repos. Stay in this tree.

## Loop

1. Pick the example (`--example` or the one you were given).
2. Read `examples/<name>/SPEC.md`. Those bullets are the spec.
3. Read `examples/<name>/src/` (the product) and `examples/<name>/lean/<Pkg>/Statements.lean` (the Lean model). They must stay in lockstep.
4. Try to produce a violation certificate:
   - `python3 scripts/gate.py --example <name>`
   - or write `lean/Scratch/Violation.lean` yourself: `theorem ... : ¬ Property Impl := by intro h; simpa [Impl] using h ...`
5. If the certificate needs a helper fact about lists / filters / sums / transitions:
   - `python3 scripts/corpus.py list --example <name>`
   - `python3 scripts/corpus.py add-lemma --example <name> --name <snake_name>`
   - fill the stub, make it compile (`lake build` in that example's `lean/`)
   - import it from the certificate or from `<Pkg>.Corpus`
   - retry the gate
6. Stop when Lean accepts a violation (deny) or you cannot find one (approve).

## Rules

- Statements only in the default lib. Do not put `theorem impl_satisfies` next to `Impl`.
- Optional safety proofs go in `Safe.lean` (not a default target).
- Violation certificates: `simpa [Impl] using h nats...`. Do not add `exact this` after simp already closed.
- Do not `sorry` a deny certificate. The kernel must accept a real proof.
- Corpus lemmas must not mention `Impl`. The deny path mutates `Impl`; facts about the current model go in `Safe.lean`.
- Tiny lemmas. One fact per file. Name them after the fact, not the ticket.
- If Python finds a witness but Lean rejects the certificate, the model is out of sync with `src/`. Fix the model, then retry.
