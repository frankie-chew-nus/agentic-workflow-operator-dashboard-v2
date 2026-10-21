"""One-pass local T04/T05/T09/T10 reconciliation; read-only, fail-closed.

Run against local evidence directory and dashboard DB. Reports facts and gaps,
never promotes a policy approval or synthetic test to a verified live control.
"""
import argparse,hashlib,json,sqlite3,datetime
from pathlib import Path
NAMES={
 "T04":"T04_OPERATOR_POLICY_APPROVAL_2026-10-21.md",
 "T05":"T05_OPERATOR_POLICY_APPROVAL_2026-10-21.md",
 "T09":"T09_DISTINCT_CANDIDATE_COUNTING_APPROVAL_2026-10-21.md",
 "T10":"T09_T10_OPERATOR_POLICY_APPROVAL_2026-10-21.md"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(root,db):
 root=Path(root).resolve();db=Path(db).resolve()
 result={"kind":"READ_ONLY_RECONCILIATION","time_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "controls":{},"dashboard_release_ledger":[],"candidate_states":[],"activation_authorized":False,
 "manifest_modified":False,"database_modified":False}
 for code,name in NAMES.items():
  p=root/name
  result["controls"][code]={"policy_file_present":p.is_file(),"policy_sha256":sha(p) if p.is_file() else None,
   "operational_status":"HOLD_UNVERIFIED"}
 if db.is_file():
  c=sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)
  try:
   for row in c.execute("SELECT research_id,candidate_id,decision,created_at,id FROM decisions WHERE decision='RELEASE_TO_C' ORDER BY created_at"):
    result["dashboard_release_ledger"].append(dict(zip(("research_id","candidate_id","decision","created_at","decision_id"),row)))
   for row in c.execute("SELECT id,research_id,version,state FROM candidates ORDER BY id"):
    result["candidate_states"].append(dict(zip(("candidate_id","research_id","version","state"),row)))
  finally:c.close()
 else:result["db_error"]="DASHBOARD_DB_NOT_FOUND"
 # Policy approvals do not prove resource contracts, dependencies, ledger completeness or change authority.
 result["controls"]["T04"]["required_next_evidence"]=["versioned resource inventory","ATR derivation contract","Previous_Day_OHLC contract"]
 result["controls"]["T05"]["required_next_evidence"]=["actual runtime dependency inventory","inspectability and prohibition review"]
 result["controls"]["T09"]["required_next_evidence"]=["reconcile all B-to-C decision sources","verify historical decision provenance"]
 result["controls"]["T10"]["required_next_evidence"]=["Operator-owned policy version and change-decision register"]
 result["status"]="HOLD_REVIEW_REQUIRED"
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--evidence-dir",required=True)
 p.add_argument("--dashboard-db",required=True)
 p.add_argument("--output",required=True)
 a=p.parse_args()
 data=inspect(a.evidence_dir,a.dashboard_db)
 dest=Path(a.output).resolve()
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():raise SystemExit("REFUSE_OVERWRITE_EXISTING_RECONCILIATION")
 dest.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
 print("Report:",dest)
 print("Release records:",len(data["dashboard_release_ledger"]))
 print("Status:",data["status"])
