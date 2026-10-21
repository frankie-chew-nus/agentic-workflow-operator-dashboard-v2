"""Read-only T09 cross-check of dashboard release event with C evidence.

Does not authenticate the Human actor or infer full historical completeness.
Prints limited identifiers, hash checks and presence flags; never mutates files.
"""
import json,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=ROOT/"evidence"/"operator.db"
CROOT=ROOT.parent/"gate2_c_controller"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def main():
 if not DB.is_file():raise SystemExit("Dashboard DB missing")
 con=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 con.row_factory=sqlite3.Row
 try:
  releases=[dict(r) for r in con.execute("SELECT id,research_id,candidate_id,created_at FROM decisions WHERE decision='RELEASE_TO_C' ORDER BY created_at")]
  states={r["id"]:{"state":r["state"],"stage":r["stage"]} for r in con.execute("SELECT id,state,stage FROM candidates")}
 finally:con.close()
 result=[]
 for r in releases:
  cid=r["candidate_id"]
  # Exact candidate-scoped roots only. Presence is not proof of consumption.
  candidates=[CROOT/"evidence"/"semantic_gate"/(cid+"_release.json"),
              ROOT.parent/"gate2_operator_app_v1"/"evidence"/"b_resume"/cid/"b_corrected_release.json"]
  artifacts=[]
  for p in candidates:
   d=None
   if p.is_file():
    try:d=json.loads(p.read_text(encoding="utf-8"))
    except (OSError,ValueError):pass
   artifacts.append({"kind":p.name,"exists":p.is_file(),"sha256":sha(p) if p.is_file() else None,
    "record_state":d.get("state") if isinstance(d,dict) else None,
    "candidate_id_matches":d.get("candidate_id")==cid if isinstance(d,dict) else None})
  result.append({"decision_id":r["id"],"research_id":r["research_id"],"candidate_id":cid,
    "decision_time":r["created_at"],"candidate_current_state":states.get(cid),
    "artifacts":artifacts,"human_identity_authenticated":False,
    "C_consumption_proven":False})
 print(json.dumps({"mode":"READ_ONLY_T09_RELEASE_TO_C_EVIDENCE_CROSSCHECK",
  "dashboard_db_sha256":sha(DB),"record_count":len(result),"records":result,
  "historical_completeness_verified":False,"ledger_approved":False,
  "verdict":"HOLD_PENDING_OPERATOR_RECONCILIATION",
  "writes_performed":False,"production_authority":False},indent=2))
if __name__=="__main__":main()
