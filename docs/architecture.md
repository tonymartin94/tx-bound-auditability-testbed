# Architecture and Security Model

This testbed implements a minimal system to demonstrate **decision-bound execution** and **failure-aware auditability**.

The goal is not to prevent all failures, but to make violations and suppression **externally observable and non-deniable**.

---

## 1. State Machine

Every transaction follows this lifecycle:

UNDECIDED → DECIDED → EXECUTED → ANCHORED

- **UNDECIDED**: no policy/compliance decision exists yet
- **DECIDED**: a cryptographically bound decision receipt is issued
- **EXECUTED**: execution only allowed if receipt is valid and payload matches
- **ANCHORED**: commit of the decision is appended to an immutable-ish log asynchronously

Anchoring is intentionally asynchronous and may fail.

---

## 2. Components

### DecisionService
Issues a **DecisionReceipt** containing:

- tx_id
- decision (APPROVE / REJECT)
- decided_at timestamp
- policy_version
- payload_hash
- nonce
- commit hash
- HMAC over the receipt

This binds *what was checked* to *what must be executed*.

---

### ExecutionService

Enforces:

- Decision-before-execution
- Replay resistance (tx_id can execute only once)
- TOCTOU protection (payload hash must match receipt)
- Records all attempts into the **Executions log**

This log represents **what the system claims happened**.

---

### AnchorWorker

Takes commit hashes from executed transactions and writes them to the **Anchors log**.

This simulates anchoring to an immutable system (e.g., blockchain, transparency log).

Anchoring may be:
- delayed
- dropped (suppression)
- successful

---

### Watcher

Continuously reconciles:

Executions log  VS  Anchors log

If an executed commit does not appear in the anchors log after a deadline, it is flagged as:

**MISSING_ANCHOR_AFTER_DEADLINE**

This is the core of **failure-aware auditability**.

---

## 3. Logs as Evidence

| Log | Meaning |
|----|----|
| Executions | What the system says was executed |
| Anchors | What was externally committed |
| Watcher findings | Evidence of suppression or delay |

The security property emerges from comparing these logs.

---

## 4. Attacks Demonstrated

### Replay
Same tx_id reused → execution blocked and logged.

### TOCTOU
Decision made on payload A, execution attempts payload B → blocked and logged.

### Suppression
Execution occurs but commit never appears in anchors → detected by watcher.

---

## 5. Security Insight

Traditional systems assume:
> “If anchoring fails, we lose integrity.”

This testbed demonstrates:
> “If anchoring fails, we gain evidence of failure.”

That is the key research insight.
