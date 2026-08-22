# The plugin

A PR lands. We retell it in Lean. A person reads the retelling.

Then we try to prove one of two endings:

- **still matches** — the old rules still hold
- **rules changed** — the PR updates the contract, and that update is the review

Lean cannot read the other language. The retelling is what we check in.
If a person cannot agree with the retelling, stop.

`retell.py` prints that card from the files already in this repo.
A GitHub Action posts it on the PR.
