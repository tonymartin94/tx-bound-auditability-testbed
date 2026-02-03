# Decision-Bound Execution + Failure-Aware Auditability (Python Research Testbed)

This repository contains a minimal, runnable research artefact demonstrating how to bind policy/compliance decisions to transaction execution and make anchoring failures externally observable.

## Core Idea

UNDECIDED → DECIDED → EXECUTED → ANCHORED

Anchoring is asynchronous and may fail. The system detects these failures by reconciling executed transactions against anchored commitments.

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
