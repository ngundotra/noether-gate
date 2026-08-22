# Spec — medium-orders

An order is a state machine:

`pending → paid → shipped → delivered`

Cancel is allowed only from `pending` or `paid`.

| id | Bullet |
|---|---|
| no-skip | A transition may not skip a step. `pending` cannot jump to `shipped` or `delivered`. `paid` cannot jump to `delivered`. |
| no-backwards | A transition may not move backwards along the happy path, and a cancelled order stays cancelled. |
| cancel-only-open | `cancelled` is only reachable from `pending` or `paid`. Shipped / delivered / cancelled orders cannot be cancelled. |
