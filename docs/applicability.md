Applicability of the Testbed to Systems, Protocol, and Decentralized Security Research

This research artefact was designed to explore how cryptographic evidence can enforce system invariants and how failures in anchoring or logging mechanisms can become externally observable signals rather than silent integrity loss.

While implemented as a minimal Python testbed, the model captures core problems studied across multiple security research domains.

1. Relevance to Security Protocol Research

The system can be viewed as a security protocol with:

Clearly defined roles (Client, DecisionService, ExecutionService, AnchorWorker, Watcher)

Message exchanges (decision receipt, payload, commit)

Enforced invariants (decision-before-execution, replay resistance, TOCTOU protection)

Explicit adversary model (rational operator)

This makes the artefact relevant for formal modelling and verification of protocol invariants.

2. Relevance to Decentralized Systems Security

The testbed models challenges central to decentralized platforms:

Decentralized Security Problem	Modelled in Testbed
Verifiable state changes	Commit hash binds decision to execution
Asynchronous, unreliable anchoring	AnchorWorker delay/suppression
Adversarial operators	Rational operator model
Tamper-evident logging	Executions vs Anchors reconciliation
Minimal data exposure	Payload hashes only

This directly relates to secure logging, auditability, and integrity guarantees in blockchain and distributed ledger environments.

3. Relevance to Secure Logging and Auditability

The core security property emerges not from a single log, but from comparing:

Executions log − Anchors log

This models how audit systems can derive integrity from reconciliation rather than assuming perfect logs.

4. Relevance to Trustworthy Information Processing

The artefact demonstrates how:

Decisions are cryptographically bound to actions

Failures in evidence recording become detectable

System trust can emerge from failure observability

5. Relevance to Cyber-Physical and Platform Security

Any system where:
                a decision must provably precede an irreversible action

can apply this model, including robotics control, storage platforms, regulated systems, and distributed services.

Key Insight

Traditional systems assume:
                If logging or anchoring fails, integrity is lost.
This model shows:
                If logging or anchoring fails, integrity violations become observable and non-deniable.


This artefact is intentionally minimal to clearly expose these security properties and serve as a basis for further formal, distributed, or platform-level research.

