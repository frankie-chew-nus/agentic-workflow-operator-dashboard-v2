# MSI5002 Agentic Workflow Operator Dashboard — Source Package

Academic source-code release of the A→E XAUUSD M1 research workflow. **Not a live-trading application.** The B→C release path is deliberately HOLD-only while T04/T05/T09/T10 operational evidence remains incomplete.

## Prerequisites

- Python 3.11 or later (tested in a clean Linux environment with Python 3.13; Windows validation is separate).
- Git (or download the repository ZIP).
- Local permission to listen on port 8787.
- Optional external AI/data integrations need their own credentials and local market-data files; these are **not** supplied.

The dashboard and bundled standard-library tests do not require third-party packages. Some optional engine integrations may require additional packages, such as MetaTrader5, which is Windows/terminal-dependent and is **not installed by default**.

## Download and run

Windows PowerShell or CMD:

```cmd
git clone https://github.com/frankie-chew-nus/agentic-workflow-operator-dashboard-v2.git
cd agentic-workflow-operator-dashboard-v2
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest test_ae_build_contract test_b_operational_boundary test_actual_dashboard_hold_no_pin -v
.venv\Scripts\python.exe gate2.py
```

For this pre-release import branch, add `--branch build/gate2-source-import` to `git clone`, or switch to that branch after cloning. These commands are for `main` **after** acceptance and merge.

Linux/macOS:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest test_ae_build_contract test_b_operational_boundary test_actual_dashboard_hold_no_pin -v
.venv/bin/python gate2.py
```

Open http://127.0.0.1:8787/ and keep the terminal running. Press Ctrl+C to stop.

## Source layout

- `gate2.py`: Operator dashboard, SQLite initialization and stage routing.
- `operator_paths.json`: repository-relative engine paths.
- `gate2_operator_app_v1/`: bundled B workflow.
- `gate2_c_controller/`: bundled C workflow.
- `b_operational_boundary.py`: active fail-closed B→C inspector.
- `d_*.py`, `e_*.py`: sandbox D/E modules.
- `test_ae_build_contract.py`, `test_b_operational_boundary.py`, `test_actual_dashboard_hold_no_pin.py`: core acceptance suite.
- `gate2_evidence/`: prior engineering evidence and test outputs, **not** newly reproduced market outcomes.

## Limitations and data

A fresh checkout creates a **new local SQLite database** with illustrative initial candidates; it does **not** reproduce the historical CAND-B-002 ledger from the developer's machine. Do not confuse initialized sample state with historical execution evidence. Actual A/B model calls and C-stage executions require configured provider endpoints, verified strategy inputs, and market-data manifests not included here. C remains review-required; D/E are sandbox-only. No broker integration or live commissioning is authorized.

This repository intentionally excludes personal secrets, local databases, raw market datasets, generated C workspaces, PIN experiments, and obsolete dashboard-copy test fixtures. The old engineering repository retains historical experiments and failure records.

## Evidence integrity

In-vitro regression PASS is evidence of control behavior, **not** a trading strategy PASS or production authorization. T04/T05/T09/T10 operational HOLDs remain. Existing evidence in `gate2_evidence/` must be read with its original limitations. Never use the dashboard to claim a fresh C/D/E success without a corresponding evidence chain.

## Repository status

This import branch is under portability review. Do not treat it as professor-ready until fresh-install acceptance is completed and the reviewed branch is merged to `main`.
