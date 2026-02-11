# Research Statement — Tony Martin
## Research Interest

My research interest lies in **systems security at the intersection of decision processes, cryptographic evidence, and auditability under failure**.

I am particularly interested in how systems can be designed so that:
- security decisions are cryptographically bound to actions,
- failures in audit or anchoring mechanisms do not silently degrade integrity,
- and adversarial operational behaviour becomes externally observable rather than undetectable.

This direction sits at the intersection of:

- Applied Cryptography
- Systems Security
- Trustworthy Information Processing
- Privacy-by-Design Architectures
- Failure Semantics in Distributed Systems

---

## Motivation

Many real-world systems — financial systems, regulatory platforms, healthcare workflows, supply chains, robotics control, and distributed services — rely on a common pattern:

 A decision is made, and later an action is executed based on that decision.

However, these systems often assume that audit logs, transparency logs, or blockchains will reliably record evidence of those decisions. When anchoring fails, is delayed, or is suppressed, the integrity of the system quietly degrades.

I am interested in a different question:

 Can systems be designed such that anchoring failures themselves become detectable signals of abnormal behaviour?

---

## Research Artefact

To explore this, I built an open-source research testbed:

**Decision-Bound Execution + Failure-Aware Auditability**  
https://github.com/tonymartin94/tx-bound-auditability-testbed

This artefact demonstrates:

- Decision-before-execution enforcement
- Replay resistance
- TOCTOU detectability
- Suppression detectability through set reconciliation
- Privacy-preserving commitments (no sensitive data in anchors)

The system models a transaction lifecycle:

UNDECIDED → DECIDED → EXECUTED → ANCHORED

Where anchoring is asynchronous and may fail, but failures become **externally observable**.

A preprint describing this work is being submitted to arXiv.

---

## Key Insight

Traditional systems treat anchoring as an integrity guarantee.

My work explores a different model:

 Anchoring as a mechanism for failure-aware auditability.

Instead of assuming perfect logs, the system gains security properties from the comparison between:

- what the system claims happened, and
- what was externally committed.

---

## Future Research Direction

I would like to extend this work into:

- Formal modelling of decision-bound systems
- Cryptographic constructions for commitment and auditability
- Failure semantics in adversarial environments
- Privacy-preserving evidence systems
- Applications to cyber-physical systems, distributed services, and regulatory infrastructures

I am particularly interested in working with groups researching:

- Automated verification of security properties
- Applied cryptography and protocol design
- Trustworthy distributed systems
- Security of cyber-physical and socio-technical systems

---

## Goal

My goal is to pursue doctoral research focused on designing systems where:

 Security is derived not from assuming components always work, but from making their failures observable, attributable, and non-deniable.
