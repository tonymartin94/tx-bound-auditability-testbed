# Threat Model and Failure Semantics

## Adversary Model

We assume a rational operator adversary who:

- May attempt replay, suppression, or TOCTOU attacks
- Controls execution and anchoring subsystems
- Cannot break cryptographic primitives
- Cannot rewrite the append-only audit log once written
- Can delay or drop anchoring events

## Security Goal

This system does not aim for perfect prevention. Instead, it aims to:

- Make violations externally observable and non-deniable
- Provide explicit failure semantics when anchoring is delayed or suppressed

## Attacks Demonstrated

1. Replay — reusing a valid receipt for the same transaction ID
2. TOCTOU — decision made on payload A, execution attempted with payload B
3. Suppression — execution occurs but anchoring never happens

## Observability Mechanism

The system relies on set reconciliation:

- The Executions table represents what executed
- The Anchors table represents what was committed
- The Watcher flags executed commits missing from anchors after a deadline
