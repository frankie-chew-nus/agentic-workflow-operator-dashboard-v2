"""Read-only final B integration readiness audit using actual local evidence.

This is a *blocking gate*, not deployment. No strategy imports, B execution,
SQLite writes, external APIs, or automatic approvals. All unverified controls HOLD.
"""
import csv,datetime,hashlib,json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DASH=Path(__file__).resolve().parent
DATA=ROOT/"data"/"stage1_xauusd_m1.csv"
DB=ROOT/"gate2_operator_app_v1"/"evidence"/"operator.db"
REGISTER=ROOT/"gate2_c_controller"/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"
OUT=DASH/"gate2_submission_evidence"/"governance_tests"/"w6_live_input_readiness.json"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def main():
 if OUT.exists():raise SystemExit("Existing report: refusing overwrite")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=DASH,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 required=[DATA,DB,REGISTER]
 if any(not p.is_file() for p in required):raise SystemExit("Missing input; no report generated")
 with DATA.open("r",encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f,delimiter="\t")
  fields=set(reader.fieldnames or [])
  expected={"<DATE>","<TIME>","<OPEN>","<HIGH>","<LOW>","<CLOSE>"}
  if not expected.issubset(fields):raise SystemExit("OHLC columns missing")
  count=0;invalid=0;nonincreasing=0;previous=None
  for row in reader:
   count+=1
   try:
    ts=datetime.datetime.strptime(row["<DATE>"]+" "+row["<TIME>"],"%Y.%m.%d %H:%M:%S")
    o,h,l,c=[float(row[k]) for k in ("<OPEN>","<HIGH>","<LOW>","<CLOSE>")]
    import math
    if not all(math.isfinite(x) for x in (o,h,l,c)) or h<max(o,l,c) or l>min(o,h,c):raise ValueError("OHLC invalid")
    if previous is not None and ts<=previous:nonincreasing+=1
    previous=ts
   except (ValueError,TypeError,KeyError):invalid+=1
 register=json.loads(REGISTER.read_text(encoding="utf-8"))
 required_inputs=sorted({str(x) for c in register.get("candidates",[]) for x in c.get("required_inputs",[])})
 db=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 try:
  candidate_states=[{"state":s,"count":n} for s,n in db.execute("SELECT state,COUNT(*) FROM candidates GROUP BY state")]
  decision_types=[{"type":s,"count":n} for s,n in db.execute("SELECT decision,COUNT(*) FROM decisions GROUP BY decision")]
 finally:db.close()
 policies=["T04_OPERATOR_POLICY_APPROVAL_2026-10-21.md","T05_OPERATOR_POLICY_APPROVAL_2026-10-21.md","T09_T10_OPERATOR_POLICY_APPROVAL_2026-10-21.md"]
 approvals=DASH/"gate2_submission_evidence"/"governance_tests"
 policy_records={p:{"present":(approvals/p).is_file(),"sha256":sha(approvals/p) if (approvals/p).is_file() else None} for p in policies}
 ohlc_pass=count>0 and invalid==0 and nonincreasing==0
 controls={
  "T04":{"policy_definition_recorded":policy_records[policies[0]]["present"],"ohlc_structural_check":"PASS" if ohlc_pass else "HOLD","ATR_contract":"UNVERIFIED","Previous_Day_OHLC_contract":"UNVERIFIED","resource_inventory":"NOT_APPROVED","verdict":"HOLD"},
  "T05":{"policy_definition_recorded":policy_records[policies[1]]["present"],"approved_live_dependency_inventory":"UNVERIFIED","verdict":"HOLD"},
  "T09":{"policy_definition_recorded":policy_records[policies[2]]["present"],"reconciled_commission_release_ledger":"UNVERIFIED","verdict":"HOLD"},
  "T10":{"policy_definition_recorded":policy_records[policies[2]]["present"],"independently_authenticated_human_decision_register":"UNVERIFIED","verdict":"HOLD"}
 }
 result={"evidence_class":"READ_ONLY_LIVE_INPUT_READINESS","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "branch":branch,"commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=DASH,text=True).strip(),
  "dataset":{"sha256":sha(DATA),"rows":count,"invalid_rows":invalid,"nonincreasing_timestamps":nonincreasing,"raw_values_exported":False},
  "frozen_register_sha256":sha(REGISTER),"required_inputs":required_inputs,
  "db_sha256":sha(DB),"db_candidate_state_counts":candidate_states,"db_decision_type_counts":decision_types,
  "approval_record_hashes":policy_records,"controls":controls,
  "overall":"HOLD_NOT_READY_FOR_ACTIVE_INTEGRATION",
  "note":"Historical DB labels do not establish release authority. Approved policy definitions are not approved live inventories.",
  "active_adapter_modified":False,"production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Dataset rows:",count,"invalid:",invalid,"nonincreasing:",nonincreasing)
 print("T04/T05/T09/T10:",*[controls[k]["verdict"] for k in ("T04","T05","T09","T10")])
 print("Overall:",result["overall"])
 print("Evidence:",OUT.relative_to(DASH))
if __name__=="__main__":main()
