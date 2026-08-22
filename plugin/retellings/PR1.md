# Example: rules changed (retry sends twice)

The send now takes a retry count. Each retry sends `amount` again if the source can pay.

- Start 10 and 10, send 5 once: (5, 15).
- Start 10 and 10, send 5 with one retry: (0, 20).
- The sum is still 20. The extra on dest came from source.

The old “moves amount once” rule is false after a retry. That is a contract change, not a mint.
