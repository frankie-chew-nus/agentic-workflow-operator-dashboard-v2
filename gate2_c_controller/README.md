# Permanent C Controller

This replaces the disposable controller-vN pattern. Future capabilities will be added to this same controller.

Commands:
```
py c_controller.py self-test
py c_controller.py build CAND-B-001
py c_controller.py build-all
py c_controller.py stage1
```

Only `self-test` is enabled initially. The others intentionally return `NOT_YET_ENABLED` until the delegation architecture passes.

The DMR describes work. Deterministic Python independently classifies disclosure. External coding is called only after GREEN release. All proposed commissions are captured locally before the gate.

Run:
```cmd
py c_controller.py self-test --evidence-dir evidence\self_test
```

Expected:
`SELF_TEST_READY`, `classification=GREEN`, `external_agent_called=true`, `acceptance_test=PASS`.

Afterward rerun the Gate 2 Evidence Collector.
