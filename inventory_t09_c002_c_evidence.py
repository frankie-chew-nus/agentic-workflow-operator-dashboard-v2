"""Read-only CAND-B-002 C-evidence inventory for T09 release reconciliation.

No execution, mutation, payload export or assumption that an artifact proves
consumption of dashboard RELEASE_TO_C decision DEC-F34D70261D.
"""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
CID="CAND-B-002"
DECISION="DEC-F34D70261D"
DB=ROOT/"evidence"/"operator.db"
BASES=[ROOT/"evidence"/"c_runs",PROJECT/"gate2_c_controller"/"evidence",PROJECT/"gate2_operator_app_v1"/"evidence"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def main():
 if not DB.is_file():raise SystemExit("Dashboard DB missing")
 c=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 try:
  rows=c.execute("SELECT id,research_id,candidate_id,decision,created_at FROM decisions WHERE id=?",(DECISION,)).fetchall()
  if len(rows)!=1 or rows[0][2]!=CID or rows[0][3]!="RELEASE_TO_C":raise SystemExit("Decision mismatch")
  jobs=c.execute("SELECT kind,state,return_code,created_at,started_at,finished_at FROM jobs WHERE candidate_id=? ORDER BY created_at",(CID,)).fetchall()
  artifacts=c.execute("SELECT kind,sha256 FROM artifacts WHERE candidate_id=?",(CID,)).fetchall()
 finally:c.close()
 found=[]
 for base in BASES:
  if not base.is_dir():continue
  for p in base.rglob("*"):
   if not p.is_file():continue
   rel=p.relative_to(base)
   if CID not in str(rel):continue
   if p.suffix.lower() not in (".json",".md",".txt"):continue
   if len(found)>=100:break
   entry={"root":str(base.relative_to(PROJECT)),"relative_path":str(rel),"sha256":sha(p)}
   if p.suffix.lower()==".json" and p.stat().st_size<2000000:
    try:
     obj=json.loads(p.read_text(encoding="utf-8"))
     if isinstance(obj,dict):
      entry["keys"]=sorted(obj.keys())[:35]
      entry["state"]=obj.get("state") if isinstance(obj.get("state"),str) else None
      entry["references_decision_id"]=DECISION in json.dumps(obj)
    except (ValueError,OSError,UnicodeError):entry["json_parse"]="UNAVAILABLE"
   found.append(entry)
 report={"mode":"READ_ONLY_T09_C002_C_EVIDENCE_INVENTORY","decision_id":DECISION,
 "candidate_id":CID,"dashboard_decision_time":rows[0][4],
 "jobs":[{"kind":j[0],"state":j[1],"return_code":j[2],"created_at":j[3],"started_at":j[4],"finished_at":j[5]} for j in jobs],
 "dashboard_artifact_kinds":[{"kind":a[0],"recorded_hash_present":bool(a[1])} for a in artifacts],
 "files":found,"truncated":len(found)>=100,
 "C_consumption_verified":False,"human_identity_authenticated":False,
 "historical_completeness_verified":False,"ledger_approved":False,
 "verdict":"HOLD_PENDING_OPERATOR_RECONCILIATION","writes_performed":False,"production_authority":False}
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
