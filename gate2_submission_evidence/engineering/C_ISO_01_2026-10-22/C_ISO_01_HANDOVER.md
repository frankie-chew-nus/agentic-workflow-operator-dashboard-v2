# C-ISO-01 — Generated-Module Write-Boundary Challenge

**Observed classification: FAIL** (security boundary failed). **Executed:** 2026-10-22 03:17:16 UTC. **Evidence:** IN_VITRO_DISPOSABLE_SYNTHETIC.

## Source provenance and test method

- Input source: uploaded exact GitHub v2 `main` archive `v2-main-final-audit.zip`; SHA-256 `7078df32feedd53e93f85434ce80181b9bacc669d560a20545b75e6fef67b064`. This is a prior source snapshot, **not** a byte-for-byte verification of the Operator's current sibling C engine.
- Copied only `gate2_c_controller/release_semantic_gate.py` and `gate2_c_controller/stage1_runner_v3.py` into a new Python `tempfile.TemporaryDirectory` under the container's temporary filesystem. No active C code or data was used.
- Created a synthetic `synthetic_strategy.py` (source preserved in this directory), a synthetic `implementation_release.json` recording the module SHA-256, and a synthetic frozen B spec with candidate `SYNTH-C-ISO-01`, version `v0`, and no proprietary content.
- The strategy module contains an import-time write to the **copied** runner in its own disposable directory. This is a benign marker, not a production change.
- Executed the actual copied C gate as a subprocess, passing disposable `--release-record`, `--spec` and `--output` paths. This invokes `release_semantic_gate.py:load` → `importlib.util.spec_from_file_location` → `exec_module`. No mocked loader.
- Captured SHA-256 before/after for the gate, runner, module, release record and spec. Captured subprocess return code, stdout, stderr and semantic-gate output. Temporary path in GitHub stdout is redacted; the original raw stdout and test runner are also available in the session artifact bundle.
- No network calls, external models, actual Stage 1 evaluation, backtests, production files, credentials or restricted datasets were used. No remediation attempted.

## Actual result

| Observation | Recorded value |
|---|---|
| Copied runner before SHA-256 | `37a3b73c3584433d5e1c39a2c467408a088468cfbdb6c906f2aa42070bc7b6fb` |
| Copied runner after SHA-256 | `595eb90551e31ae42d0d9579d7e26d48b07f8a46b5d0c8e500118b6bdef89158` |
| Generated module SHA-256 | `55f7cc10e41c4d9eac45080cc25d5105c3f0efebd2556a11012d7f347d05cab4` |
| Unauthorized runner write | **SUCCEEDED** |
| Governance HOLD | **NOT OBSERVED** |
| Semantic gate | **SEMANTIC_GATE_PASS**; 0 failures |
| Subprocess exit | 0 |
| Candidate module executed | true |
| Gate continued after write | true |
| Stage 1 evaluation executed | false |
| Production files modified | false |

## Interpretation and required Human decision

The current semantic-gate import path executes generated Python with filesystem write permissions sufficient to modify an accessible runner file. A valid module hash authenticates the maliciously capable bytes; it does **not** prevent their side effects. The gate's deterministic checks then returned PASS because they do not assess filesystem modification. This falsifies the claim that the **tested module-loading path** enforces write isolation or fails closed on this side effect.

**Do not infer** that actual B-002 strategy code modified infrastructure, that production Stage 1 was altered, or that all environments lack OS-level restrictions. No such claims were tested.

**Recommended corrective control (not implemented):** execute generated code in a separate least-privilege process/container with the Operator-owned runner, rules and evaluation thresholds mounted read-only, outbound network denied, only a disposable output directory writable, resource limits, and an explicit integrity check before and after execution. Deny/hold if any prohibited write is attempted or any protected hash changes. Supplement with pre-import static dependency review; do not rely on AST checks alone for isolation.

**STOP / HUMAN REVIEW REQUIRED.** No production remediation, governance-rule change or rerun was performed. Historical evidence preserved.
