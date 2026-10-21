# W6 Governance Evidence Report — T01–T10

**Purpose:** Gate 2 Parts 5 and 6. **Scope:** Historical B v2 candidate checker and current dashboard transition guard; NOT an end-to-end production B→C certification.

## Method and observed results

The original W6.3 T01–T10 outcomes were **synthetic paper walkthroughs**. Subsequent executable tests were run locally by the Operator, with JSON results and provenance committed to this branch. Each result is scoped to the Python function actually exercised.

| W6 ID | Paper expectation | Executable observation | Assessment |
|---|---|---|---|
| T01 | Valid candidate RELEASE | Historical `b_v2.checks` accepted controlled valid specification | PASS — candidate-level only |
| T02 | Ambiguous specification HOLD | Historical checker rejected signed-body ambiguity | PASS — specific ambiguity only |
| T03 | Unapproved source HOLD | Historical checker rejected `SRC-X-099` | PASS — source-reference check only |
| T04 | Missing resource HOLD | Historical checker returned no failures for unavailable test library | FAIL — historical checker enforcement gap |
| T05 | Prohibited black-box HOLD | Historical checker returned no failures for opaque dependency | FAIL — historical checker enforcement gap |
| T06 | Missing Human release HOLD | `workflow_matrix.allowed(...,human=False)` returned HOLD | PARTIAL — transition-guard check |
| T07 | Human silence remains HOLD | Repeated calls with `human=False` returned HOLD | PARTIAL — no elapsed-time or reminder-system test |
| T08 | Corrected v2 rechecked, v1 retained | Identity and hash mismatches were blocked | PARTIAL — version retention/recheck unverified |
| T09 | Fourth candidate HOLD | Transition guard authorized without commission-level release count input | GAP — guard lacks aggregate-limit context |
| T10 | Unauthorized AI rule change denied | Transition guard authorized without actor/policy-change context | GAP — guard lacks rule-change provenance |

**Interpretation:** T04–T05 are reproducible failures of the *historical* checker. T09–T10 expose missing inputs in the transition guard, not proven end-to-end policy violations. A passing test of a narrow guard does not upgrade the original paper test into a fully implemented governance scenario.

## Verified GitHub evidence and provenance

| Evidence file (in this folder) | Execution commit | GitHub blob SHA |
|---|---|---|
| `w6_t01_t03_result.json` | `91197140a75f4754e86e2a5337bbdedc4b084cfa` | `737fe0f1adf5d88b2b00eb85d4d4a2fe36ff6942` |
| `w6_t04_t05_findings.json` | `e32eebd077a919e53da6ab1e7b9af3a87ef0bcfa` | `96aa6828b21b217f5797acafc7817ffff6c4534b` |
| `w6_t06_t10_result.json` | `c26a4d4629f548c4d71c71078b35912bea2d991f` | `6abcce34c4fd2bc17f8b273be9e8c39c37af8c6f` |
| `w6_t09_t10_findings.json` | `69cb34a66478889f8562f350636c9543e71c3f7e` | `72a932490219fa25196dc298059fb368020c5c85` |

**Hash note:** The values above are GitHub Git blob IDs, **not SHA-256 file-content hashes**. The individual JSON records include source/test SHA-256 hashes and sanitized-log fields. Their `raw_log_sha256` values cannot independently reconstruct the original full logs from sanitized excerpts alone.

## Limitations and next engineering work

1. Inspect the **current active B→C adapter and release path**, not just historical `b_v2.py`.
2. Add isolated negative tests for unavailable resources and prohibited dependencies to the actual active validation boundary; preserve baseline failures before any repair.
3. Test persisted Human authority, correction/version lineage, three-candidate commission limit, and unauthorized rule changes end-to-end using disposable fixtures and databases.
4. Record before/after outcomes separately; do not silently replace failed evidence with later PASS results.

**Production D/E authority:** Unchanged; this report grants none. **Strategy logic:** Unchanged. **Evidence principle:** Record what was demonstrated; never upgrade proof.


## Post-audit active boundary and isolated remediation (19 October 2026)

The dashboard invokes `gate2_operator_app_v1/b_resume_model_flow_v1_1.py` by default (unless `GATE2_B_ADAPTER` overrides it). This delegates to `b_resume.py`, `b_model_adapter.py`, `b_regression_guard.validate`, then `b_resume.py` again. The active B resume boundary was exercised with disposable SQLite databases and synthetic candidate records; it was **not** allowed to touch production evidence.

| Test | Active `b_resume.py` baseline | Proposed isolated policy |
|---|---|---|
| T04 unavailable resource | FAIL: returned 0 rather than expected HOLD | PASS: unavailable resource causes HOLD |
| T05 opaque black-box dependency | FAIL: returned 0 rather than expected HOLD | PASS: unapproved dependency causes HOLD |
| T09 fourth candidate | FAIL: returned 0 rather than expected HOLD | PASS: trusted synthetic count 3 causes HOLD |
| T10 unauthorized rule change | FAIL: returned 0 rather than expected HOLD | PASS: candidate-declared change causes HOLD |

**Baseline:** 4/4 negative integration tests failed (meaning the expected HOLD was not enforced by this boundary). The observed exit code 0 led to `B_CORRECTED_AWAITING_HUMAN_RELEASE`, **not direct C release**. These tests do not prove the full production release path is vulnerable.

**Remediation:** `b_boundary_policy_v1.py` passed **7/7 unit tests** (Operator-reported local execution). The isolated `isolated_b_policy_harness.py` passed **6/6 synthetic tests**, with its captured JSON verified in GitHub. These tests show proposed policy behavior, **not** repaired active adapter behavior.

**Trusted-input audit:** The existing SQLite database has `research`, `candidates`, `decisions`, `jobs`, and `artifacts` tables. Decision-type counts were 9 `RETURN_TO_B` and 2 `RETRY_B`. Authoritative resource inventory, dependency allowlist, commission-level release count and governance-rule-change authority were **not established**. Synthetic trusted context used by the harness must not be mistaken for production authoritative inputs.

**Backup protection:** The pre-remediation manifest records SQLite integrity `ok` for original and backup, matching table counts, and SHA-256 fingerprints of three active adapters. This is a backup verification, not proof of logical row-for-row equivalence. The original database and backups remain local.

### Additional verified evidence

- `w6_active_b_t04_t05_t09_t10_findings.json` — active-boundary 4/4 negative findings; execution commit `a278d19a15224a00ba6f9f60e61bd7d270fcfd88`; GitHub blob `4f6d83645a5a3ab6d7a5acbe8a2c89025db2cc9b`.
- `w6_pre_remediation_manifest.json` — backup/integrity and adapter-hash manifest; preservation commit `689b703`; GitHub blob `cc78a5e5e6de5f97fc307a65d7aafd334d58fb61`.
- `w6_isolated_remediation_result.json` — 6/6 isolated tests; execution commit `1d22ffcb2eac52c6637dd7787d5c40759faa8d74`; GitHub blob `b1c8838d4af766864c87534f0898334a3e73e560`.

**Operator decision:** Preserve existing workflow and negative findings; defer active integration until authoritative inputs and full-path regression tests are established. No merge into `main` is authorized. This decision is documented in the project conversation; it is not represented here as a signed Human decision artifact.

**Boundary:** No strategy logic was changed, no production D/E authority was granted, and no active B adapter was modified. The tested remediation is isolated and must not be described as production deployment.
