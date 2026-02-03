## Research summary (what this artefact shows)

This testbed demonstrates **decision-bound execution** with **failure-aware auditability**.

A transaction must present a cryptographically bound **decision receipt** before it can execute.  
Anchoring is **asynchronous** and may be delayed or suppressed; instead of assuming anchors always exist, the system makes anchoring failures **externally observable** via **set reconciliation**:

- **Executions log**: what actually executed
- **Anchors log**: what became publicly committed
- **Watcher**: flags executed commits missing from anchors after a deadline

The demo includes explicit scenarios for **Replay**, **TOCTOU**, and **Suppression**, showing which violations are blocked vs which become detectably abnormal.

# Decision-Bound Execution + Failure-Aware Auditability (Python Research Testbed)

This repository contains a minimal, runnable research artefact demonstrating how to bind policy/compliance decisions to transaction execution and make anchoring failures externally observable.

## Core Idea


UNDECIDED → DECIDED → EXECUTED → ANCHORED

Anchoring is asynchronous and may fail. The system detects these failures by reconciling executed transactions against anchored commitments.
## System diagram

```mermaid
flowchart LR
  C[Client] -->|payload| D[DecisionService]
  D -->|receipt: hmac, commit| C
  C -->|receipt and payload| E[ExecutionService]
  E -->|append| X[(Executions log)]
  E -->|enqueue commit| A[AnchorWorker]
  A -->|append maybe delayed| Y[(Anchors log)]
  W[Watcher] -->|reconcile after deadline| X
  W -->|read| Y
  W -->|report missing anchors| R[Findings]



stateDiagram-v2
  [*] --> UNDECIDED
  UNDECIDED --> DECIDED: receipt issued
  DECIDED --> EXECUTED: receipt verified
  EXECUTED --> ANCHORED: commit anchored async

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
