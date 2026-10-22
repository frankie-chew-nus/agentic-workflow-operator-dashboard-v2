# C Governance and C-ISO-01 — Reviewer Evidence Index

**Scope:** Sanitized evidence imported from the working engineering repository. Source content Git blob SHA matched for all seven imported files. This index is a navigation aid, not a new test or independent reproduction.

## C/model audit (22 October 2026)
- [C code governance audit](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_MODEL_GOVERNANCE_AUDIT_2026-10-22/C_CODE_GOVERNANCE_AUDIT.md)
- [Model hosting/interchangeability audit](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_MODEL_GOVERNANCE_AUDIT_2026-10-22/MODEL_HOSTING_INTERCHANGEABILITY_AUDIT.md)
- [10-test execution log](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_MODEL_GOVERNANCE_AUDIT_2026-10-22/local_execution_20261022T030642Z/unittest.txt)
- [Source fingerprints and findings](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_MODEL_GOVERNANCE_AUDIT_2026-10-22/local_execution_20261022T030642Z/findings.json)

**Observed:** 10/10 bounded static/configuration/mock tests passed; no production runtime isolation or live provider switching established. Original source commit: `35b4dcd`.

## C-ISO-01 (22 October 2026)
- [Engineering handover](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_ISO_01_2026-10-22/C_ISO_01_HANDOVER.md)
- [Machine-readable result and before/after SHA-256](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_ISO_01_2026-10-22/result.json)
- [stderr record](https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2/blob/build/gate2-source-import/gate2_submission_evidence/engineering/C_ISO_01_2026-10-22/stderr.txt)

**Observed:** FAIL, n=1 disposable synthetic strategy; runner modification succeeded, SHA changed, no HOLD, `SEMANTIC_GATE_PASS`. No Stage 1 run or production file modification. Original source commit: `0569d5b`.

## Reproducibility and disclosure boundary
The imported files are inspection records, not a complete self-contained rerun package. The original test runner, synthetic source and raw execution bundle were not independently verified as present in this GitHub import. The C-ISO-01 test used a prior v2 source snapshot, not a byte-identical verification of the active sibling C engine. No remediation or corrected PASS is claimed.
