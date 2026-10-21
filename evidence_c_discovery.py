"""Read-only discovery of C Stage 1 execution, equivalence and Human decisions."""
import hashlib,json,sqlite3
from pathlib import Path

def artifact(root,p):
 return {"path":p.relative_to(root).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def record(cid,version,suffix,claim,proof,observed,verdict,method,arts,n=None,denominator=None,human=None):
 return {"claim_id":"DISC-C-"+cid+"-"+version+"-"+suffix,"claim":claim,"proof_type":proof,
  "method":method,"n":n,"denominator":denominator,"expected":"independently verified result",
  "observed":observed,"verdict":verdict,"stage":"C","candidate_id":cid,
  "version":version,"human_decision":human,"artifacts":arts}

def discover_c(root):
 root=Path(root).resolve();base=root/"c_runs";claims=[]
 if not base.is_dir():return claims
 for p in sorted(base.glob("*/*/stage1_output/summary.json")):
  try:
   data=json.loads(p.read_text(encoding="utf-8"))
   if not isinstance(data,dict):continue
  except (ValueError,UnicodeDecodeError):continue
  version=p.parent.parent.name;cid=p.parent.parent.parent.name
  count=data.get("variant_count")
  valid=data.get("state")=="STAGE1_COMPLETE" and data.get("classification")=="EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS" and isinstance(count,int) and count>=0
  claims.append(record(cid,version,"EXECUTION","Stage 1 execution evidence, not strategy qualification",
   "INCOMPLETE","STAGE1_COMPLETE" if valid else str(data.get("state","UNKNOWN")),
   "HOLD","Stage 1 summary inspection; qualification not established",[artifact(root,p)],
   count if valid else None,count if valid else None))
 for p in sorted(base.glob("*/*/stage1_equivalence.json")):
  cid=p.parent.parent.name;version=p.parent.name
  try:obj=json.loads(p.read_text(encoding="utf-8"))
  except (ValueError,UnicodeDecodeError):obj={}
  # Even a claimed PASS is not independently certified by discovery.
  claims.append(record(cid,version,"EQUIVALENCE","Bounded versus full-history signal equivalence",
   "INCOMPLETE",str(obj.get("state","UNREADABLE")),"INCOMPLETE",
   "Recorded equivalence result; independent validation pending",[artifact(root,p)],
   obj.get("comparisons") if isinstance(obj.get("comparisons"),int) else None,None))
 return claims

def discover_decisions(root):
 root=Path(root).resolve();db=root/"operator.db"
 if not db.is_file():return []
 claims=[]
 try:
  conn=sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)
  try:
   rows=conn.execute("SELECT id,candidate_id,decision,rationale,created_at FROM decisions ORDER BY created_at,id").fetchall()
  finally:
   conn.close()
 except (sqlite3.Error,ValueError):return []
 for rid,cid,action,rationale,created in rows:
  claims.append({"claim_id":"DISC-HUMAN-"+str(rid),"claim":"Recorded Human decision (not independent authorization)",
   "proof_type":"INCOMPLETE","method":"read-only SQLite decision ledger query","n":1,"denominator":1,
   "expected":"decision provenance present","observed":str(action),"verdict":"INCOMPLETE",
   "stage":"C","candidate_id":cid,"version":None,
   "human_decision":{"id":rid,"action":action,"rationale":rationale,"created_at":created},
   "artifacts":[]})
 return claims
