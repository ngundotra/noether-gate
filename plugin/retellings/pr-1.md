# Retelling of PR 1 — retry a transfer

This is the understanding a person should review. If it is wrong, stop.

PR: https://github.com/ngundotra/noether-gate/pull/1

The ledger send now takes a `retries` count. The first send still moves `amount` from source to dest when the source can pay. Each retry, if the source still has enough, sends that same `amount` again.

## Allowed

- Reject the send when `amount` is bigger than the source. Nothing changes.
- On a successful first send, move `amount` from source to dest.
- If the caller asked for retries, try that same send again, up to that many times, and only while the source still has `amount`.

## Must never

- Create or destroy money. After a successful send, source + dest equals the starting pair.
- Accept an overdraft. If the first `amount` does not fit, the answer is no.

Those two money rules still hold. A retry takes from the source; it does not mint.

## A case

Start with **10** and **10**. Send **5** with **one retry**.

- One send would leave **5** and **15**.
- One send plus one retry leaves **0** and **20**.
- Dest holds 5 extra. The pair is not the old pair. Those totals no longer match a one-shot send.

The sum is still 20. The extra on dest came from source. This is sending twice, not printing money.

The spec still says a transfer moves `amount`. After this PR that line is false whenever a retry lands.

## Ending

**deny**

The old “moves `amount` once” rule is broken. Lean shows it on 10, 10, send 5, one retry. See `PR1.lean`.
