Applicability to Industrial Control Systems (ICS), SCADA, and Cyber-Physical Security
This research artefact models a security problem that directly appears in Industrial Control Systems (ICS), SCADA networks, and distributed cyber-physical infrastructures.
In such environments:
•	A supervisory controller authorizes actions
•	Field devices (PLCs, actuators, robots, sensors) execute those actions
•	Logs are distributed and often unreliable
•	Failures, delays, or malicious tampering of logs are realistic threats
•	Auditability and anomaly detection are critical for safety and integrity
The testbed captures this problem through a minimal but precise model.
Mapping the Testbed to an ICS Scenario
Testbed Component	Industrial Interpretation
DecisionReceipt	Authorization from control server / safety controller
ExecutionService	Field device performing an operation
Executions Log	Local subsystem/device log
Anchors Log	Central audit / monitoring log
Watcher	Integrity monitor / anomaly detection system
The model enforces:
          No industrial action can execute without cryptographic proof of prior authorization.
And more importantly:
          If evidence of that authorization is suppressed, delayed, or tampered with, this becomes externally observable.
Industrial Security Properties Demonstrated
Decision-Before-Execution
Relevant for machine activation, safety overrides, maintenance operations, and critical control actions.
Replay Resistance
Prevents reuse of stale authorizations — protecting against misuse of old control messages.
TOCTOU Protection
Ensures the field device performs exactly what was authorized by the controller.
Suppression Detectability
If logs from field devices or audit channels are dropped or manipulated, the system detects missing evidence.
Failure-Aware Auditability for ICS
Traditional industrial systems assume:
                     If logs are missing, integrity is lost.
This testbed demonstrates:
                    If logs are missing, the absence itself becomes evidence of abnormal behaviour.
This property is valuable for:
a)	intrusion detection in industrial networks

b)	tamper-evident audit trails

c)	forensic reconstruction after incidents

d)	integrity monitoring of distributed industrial operations

Relevance to Industrial Cybersecurity Research
This artefact provides a prototype for:
•	tamper-evident state transitions
•	cryptographic audit trails
•	anomaly detection through log reconciliation
•	secure decision-to-action correctness in cyber-physical systems

