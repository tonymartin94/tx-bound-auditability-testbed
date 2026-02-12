# Architecture and Security Model

This research artefact implements a minimal system to demonstrate a security property we call:

 **Decision-Bound Execution with Failure-Aware Auditability**

The goal is not to build a product system, but to model a class of systems where:

- A policy / compliance / authorisation decision must exist **before** execution
- Each decision is cryptographically bound to transaction-scoped evidence
- Anchoring of that evidence is asynchronous and may fail
- Failures do not silently break integrity — they become **externally observable signals**

This shifts the traditional view of anchoring from *integrity guarantee* to *failure observability mechanism*.

---

## 1. State Machine Model

Every transaction follows the lifecycle:

UNDECIDED → DECIDED → EXECUTED → ANCHORED

- **UNDECIDED** — no authorisation exists
- **DECIDED** — a cryptographically bound receipt is issued
- **EXECUTED** — execution requires receipt verification and payload consistency
- **ANCHORED** — a commitment to the decision is appended asynchronously to an append-only log

The critical design choice is that **ANCHORED is not required for execution**.

Instead, the absence of anchoring becomes meaningful.

---

## 2. System Components as Security Roles

### DecisionService — *Evidence Creator*

Produces a **DecisionReceipt** binding:

- transaction identifier
- decision outcome
- payload hash (what was checked)
- policy version
- nonce
- commit hash
- HMAC authenticity

This creates **transaction-scoped cryptographic evidence**.

---

### ExecutionService — *Invariant Enforcer*

Enforces the core invariants:

- Decision-before-execution
- Replay resistance (tx_id uniqueness)
- TOCTOU resistance (payload must match decision)
- Records all attempts in an **Executions log**

This log represents:

 *What the system claims happened*

---

### AnchorWorker — *Asynchronous Committer*

Writes commit hashes to an **Anchors log** simulating:

- transparency logs
- blockchains
- append-only audit systems

Anchoring may be:

- delayed
- dropped (suppression)
- successful

This behaviour is intentional for modelling adversarial conditions.

---

### Watcher — *External Auditor*

Performs **set reconciliation**:

Executions log  VS  Anchors log

If an executed commit does not appear in anchors after a deadline, it flags:

**MISSING_ANCHOR_AFTER_DEADLINE**

This is the mechanism that turns anchoring failure into evidence.

---

## 3. Logs as Evidence, Not Storage

| Log | Represents |
|-----|------------|
| Executions | What the system asserts occurred |
| Anchors | What was externally committed |
| Watcher findings | Evidence of suppression, delay, or failure |

Security does not come from any single log, but from **their comparison**.

---

## 4. Adversary Model

Rational operator adversary:

- May attempt replay, suppression, or TOCTOU
- Cannot break cryptographic primitives
- Cannot rewrite the anchor log once written
- Can delay or drop anchoring

This reflects realistic operational threats rather than theoretical attackers.

---

## 5. Attacks Demonstrated

### Replay
Reusing tx_id → execution blocked and recorded.

### TOCTOU
Decision on payload A, execution attempts payload B → blocked and recorded.

### Suppression
Execution occurs, but commit never appears in anchors → detected by watcher.

---

## 6. Key Security Insight

Traditional systems assume:

 “If anchoring fails, integrity is lost.”

This model demonstrates:

 **If anchoring fails, integrity violations become observable and non-deniable.**

This is the core contribution of the artefact.

---

## 7. Why This Is a Systems Security Problem

This model applies wherever:

- decisions precede actions
- auditability is required
- anchoring is unreliable or delayed
- privacy requires minimal data disclosure

Examples include fintech, supply chains, healthcare workflows, robotics control, and regulatory systems.

The artefact is intentionally minimal to expose the security properties clearly.
