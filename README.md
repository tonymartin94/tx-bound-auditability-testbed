## Abstract

This repository contains a minimal research testbed demonstrating decision-bound execution and failure-aware auditability in transaction systems.

Instead of assuming that policy/compliance decisions, execution, and anchoring occur reliably and synchronously, this artefact models anchoring as an asynchronous, failure-prone process and shows how violations such as replay, TOCTOU (time-of-check vs time-of-use), and anchoring suppression become externally observable through set reconciliation between execution logs and anchor logs.

The system enforces that a cryptographically bound decision receipt must exist before execution, while a watcher component detects missing anchors after a deadline, turning anchoring failures into verifiable evidence rather than silent integrity loss.

The testbed is intentionally small, runnable in minutes, and designed as a teaching and research artefact for applied systems security, auditability, and transparency mechanisms.

## Research summary (what this artefact shows)

This testbed demonstrates decision-bound execution with failure-aware auditability.

A transaction must present a cryptographically bound decision receipt before it can execute.  
Anchoring is asynchronous and may be delayed or suppressed; instead of assuming anchors always exist, the system makes anchoring failures externally observable via set reconciliation:

- **Executions log**: what actually executed
- **Anchors log**: what became publicly committed
- **Watcher**: flags executed commits missing from anchors after a deadline

The demo includes explicit scenarios for **Replay**, **TOCTOU**, and **Suppression**, showing which violations are blocked vs which become detectably abnormal.

# Decision-Bound Execution + Failure-Aware Auditability (Python Research Testbed)

This repository contains a minimal, runnable research artefact demonstrating how to bind policy/compliance decisions to transaction execution and make anchoring failures externally observable.

## Core Idea


UNDECIDED → DECIDED → EXECUTED → ANCHORED

Anchoring is asynchronous and may fail. The system detects these failures by reconciling executed transactions against anchored commitments.
## System diagram (text)

Transaction lifecycle:

UNDECIDED -> DECIDED -> EXECUTED -> ANCHORED

Component view:

Client
  |
  v
DecisionService  --->  issues signed decision receipt
  |
  v
ExecutionService --->  writes to Executions log (SQLite)
  |
  v
AnchorWorker     --->  writes to Anchors log (async, may fail)
  
Watcher compares:
Executions log  VS  Anchors log
and flags commits missing after a deadline.


## Security Properties Demonstrated

- Decision-before-execution enforcement
- Replay resistance
- TOCTOU (time-of-check vs time-of-use) detectability
- Suppression detectability (missing anchors)
- Privacy-by-design (only hashed payloads are anchored)

## How to Run

Normal flow:

python -u -m src.tbed.simulate --db tbed.sqlite

Suppression scenario:

python -u -m src.tbed.simulate --suppression 1.0 --deadline 2 --anchor-delay 1 --db tbed.sqlite

## What to Observe

The program prints:
- Execution audit log
- Anchor log
- Watcher results (missing anchors after deadline)

See docs/threat_model.md for the threat model.
