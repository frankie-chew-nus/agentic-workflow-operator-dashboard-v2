# B→C governance: end-to-end disposable FAIL → FIX → PASS test

Date: 2026-10-21. Scope: MSI5002 Gate 2 engineering evidence.

## Claim

The actual `gate2.py` HTTP handler routes synthetic release requests to a transactional SQLite B→C boundary in a **named disposable dashboard copy**. T04 missing resources, T05 prohibited dependencies, T09 commission limit and T10 unauthorized rule changes must HOLD. A valid, host-authorized synthetic candidate can reach `READY_FOR_C` **exactly once** in that disposable database. No C execution is queued.

## Historical FAIL (not silently reclassified)

The earlier historical B enforcement tests documented T04/T05/T09/T10 gaps: legacy B checks could allow prohibited cases. They are historical negative evidence, not current passing results. The actual production dashboard was subsequently changed to fail closed; that existing 12/12 HOLD-only acceptance is preserved separately under `gate2_evidence/AE_Acceptance_20261021T052203Z/`.

## FIX

- `gate2.py` calls `b_disposable_governed_http_release.attempt` only when the module is loaded from a directory named `w6_disposable_dashboard`, test mode is enabled by the host, and trusted context is injected directly into the module by the test harness.
- Form fields do **not** supply governance approval or control verification.
- T04/T05/T09/T10 controls, candidate identity/version, current B_REVIEW state and release history are checked under a SQLite `BEGIN IMMEDIATE` transaction.
- A positive synthetic release inserts one `RELEASE_TO_C` decision and updates only the disposable candidate to `READY_FOR_C`.
- The production dashboard path continues to use `b_operational_boundary.inspect` and remains HOLD-only.

## New observed PASS (pending local execution)

`test_b_actual_http_fail_fix_pass.py` tests T04/T05/T09/T10 denials, missing host context, and a same-candidate sequence of baseline HOLD → disposable host authorization → READY_FOR_C → duplicate denial. It runs through the real HTTP handler against disposable SQLite.

Execute once:

```cmd
git pull
py run_b2c_fail_fix_pass_acceptance.py --project-root "C:\Users\frankie chew\Desktop\5002"
```

The runner creates `5002/Gate2_Evidence/B2C_FAIL_FIX_PASS_<UTC>/acceptance.json` and `unittest.txt`, including source hashes. Archive the actual local outputs in GitHub only after the run. No PASS claim is made until then.

## Limitations

- The synthetic test host stands in for verified Operator authority. This is **in-vitro**, not live approval.
- The synthetic positive proves B→C boundary liveness, not C execution, strategy success, D validation or E commissioning.
- Historical CAND-B-002 is not touched or re-released.
- The production B→C release path remains HOLD pending operational evidence.
