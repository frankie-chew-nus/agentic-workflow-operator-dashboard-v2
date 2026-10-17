# Agentic Workflow Operator Dashboard v2

Clean local A–E prototype for XAUUSD M1 research. Python 3.11+; standard library only.

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
Copy-Item .env.example .env
python -m unittest discover -s tests -v
python app.py
```
Open http://127.0.0.1:8788/.

Set real keys in local `.env`; never commit it. In this initial prototype, configure provider credentials:
- `PERPLEXITY_API_KEY` for A
- `GEMINI_API_KEY` for B and C
- `LOCAL_DMR_BASE_URL` and optionally `LOCAL_DMR_API_KEY` for an OpenAI-compatible local DMR endpoint

Current limitations: C expects a reviewed local strategy module instead of executing generated AI code. The simulator uses a diagnostic one-bar exit model; its results are not commissionable. Provider and data integration must be validated locally. D checks development/OOS split and code identity; it does not yet implement a complete production-grade strategy-specific execution model. The app blocks commissioning until qualification evidence exists.

## Datasets
Place independently selected XAUUSD M1 CSVs at:
- `data/development.csv`
- `data/oos_restricted.csv`

Columns: `timestamp,open,high,low,close`. OOS must be a separate later period and never be shown to A/B/C. Preserve originals and access controls.

## Artifacts and audit
Run state/events are stored in local `operator.db`; hashed JSON outputs are written to `artifacts/<run_id>/`. Keep secrets and market data local.

## Safety
No broker integration or live order execution. No stage may self-approve. PASS, FAIL, HOLD are distinct outcomes.