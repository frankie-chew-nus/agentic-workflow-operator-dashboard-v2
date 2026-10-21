"""Read-only market-data capability audit for proposed B governance policy.

No strategy execution, imports of trading modules, market data disclosure or writes.
Presence of data and source-code references is NOT proof of indicator correctness.
"""
import ast,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CROOT=ROOT/"gate2_c_controller"
REG=CROOT/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"
SUFFIXES={".csv",".parquet",".feather"}
KEYS=("open","high","low","close","atr","previous_day_ohlc")

def main():
 if not REG.is_file():raise SystemExit("Frozen register missing")
 reg=json.loads(REG.read_text(encoding="utf-8"))
 required=sorted({str(v) for c in reg.get("candidates",[]) for v in c.get("required_inputs",[])})
 datasets=[]
 for base in (CROOT/"market_data",CROOT/"inputs"):
  if not base.is_dir():continue
  for p in base.rglob("*"):
   if p.is_file() and p.suffix.lower() in SUFFIXES:
    datasets.append({"type":p.suffix.lower(),"size_bytes":p.stat().st_size,"path":str(p.relative_to(ROOT))})
 # Inspect local Python source text only; no imports or execution.
 matches={k:[] for k in KEYS}
 for base in (CROOT/"market_data",CROOT):
  if not base.is_dir():continue
  files=base.rglob("*.py") if base.name=="market_data" else base.glob("*.py")
  for p in files:
   try:source=p.read_text(encoding="utf-8")
   except (UnicodeError,OSError):continue
   lower=source.lower()
   for key in KEYS:
    if key in lower and str(p.relative_to(ROOT)) not in matches[key]:
     matches[key].append(str(p.relative_to(ROOT)))
 result={"mode":"READ_ONLY_C_INPUT_CAPABILITY_AUDIT",
  "frozen_register":str(REG.relative_to(ROOT)),
  "declared_required_inputs":required,
  "dataset_files":datasets[:40],"dataset_list_truncated":len(datasets)>40,
  "source_reference_files":{k:v[:15] for k,v in matches.items()},
  "verification":{"OHLC":"NOT_VERIFIED","ATR":"NOT_VERIFIED","Previous_Day_OHLC":"NOT_VERIFIED"},
  "note":"Dataset presence and source references are discovery only; no data values or strategy logic checked.",
  "writes_performed":False,"production_authority":False}
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
