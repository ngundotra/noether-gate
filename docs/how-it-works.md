# How Noether Gate works

Open this file on GitHub (phone is fine). The diagrams render in the page.

## The deny path

CI does **not** prove the code is correct. It tries to prove a spec bullet is *violated*. If Lean accepts that proof, the PR is denied.

```mermaid
flowchart TD
  SPEC["SPEC.md<br/>human-language bullets"] --> PY["search.py<br/>small input grid"]
  PY -->|"no witness"| OK["approve<br/>we could not certify a bug"]
  PY -->|"witness"| CERT["Scratch/Violation.lean<br/>theorem: not Property Impl"]
  CORP["Corpus lemmas<br/>must not mention Impl"] --> CERT
  CERT --> LEAN["lake / Lean kernel"]
  LEAN -->|"accepts the proof"| DENY["deny the PR"]
  LEAN -->|"rejects"| SYNC["Lean model out of sync with src/"]
```

## What lives where

```mermaid
flowchart LR
  subgraph example["examples/name/"]
    SPEC["SPEC.md"]
    SRC["src/"]
    FIX["fixtures/bad_*"]
    ST["Statements.lean<br/>Impl + properties"]
    CORP["Corpus/<br/>helper lemmas"]
    SAFE["Safe.lean<br/>optional Impl proofs"]
  end
  SRC -.->|"keep in lockstep"| ST
  FIX -->|"patch Impl, expect deny"| GATE["scripts/gate.py"]
  ST --> GATE
  CORP --> GATE
  SAFE -.->|"not a default target"| ST
```

## The three examples

```mermaid
flowchart TB
  subgraph easy["easy-ledger"]
    E1["preserves-sum ← bad_ledger.py"]
    E2["no-overdraft ← bad_overdraft.py"]
  end
  subgraph medium["medium-orders"]
    M1["no-skip ← pending to shipped"]
    M2["no-backwards ← paid to pending"]
    M3["cancel-only-open ← shipped to cancelled"]
  end
  subgraph hard["hard-journal"]
    H1["refunds-bounded ← over-refund"]
    H2["refunds-reference-charge ← orphan refund"]
  end
```

## Corpus rule

The deny path **mutates** `Impl` to match a bad fixture. Any lemma that mentions `Impl` then fails to build, so the certificate never typechecks.

```mermaid
flowchart TD
  A["lemma mentions Impl?"] -->|yes| SAFE["put it in Safe.lean"]
  A -->|no| CORP["put it in Corpus/"]
  CORP --> CHK["corpus.py check"]
  CHK -->|"sorry / empty stub / uncited"| FAIL["CI red"]
  CHK -->|"Impl-free, cited, no sorry"| OK["CI green"]
```
