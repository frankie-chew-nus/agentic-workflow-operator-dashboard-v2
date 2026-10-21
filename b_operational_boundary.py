"""Active B->C boundary: inspect real evidence, fail closed without PIN.

The present build does not grant new releases. This module reports why.
Existing C-stage release history is never rewritten.
"""
import hashlib,json,sqlite3
from pathlib import Path
CONTROLS=("T04","T05","T09","T10")
def inspect(conn,candidate_id,research_id,version,evidence_dir):
 failures=[]
 candidate=conn.execute("SELECT state,research_id,version FROM candidates WHERE id=?",(candidate_id,)).fetchone()
 if candidate is None or candidate[0]!="B_REVIEW" or candidate[1]!=research_id or candidate[2]!=version:
  failures.append("CANDIDATE_STATE_COMMISSION_VERSION_MISMATCH")
 rows=conn.execute("SELECT id,candidate_id,decision,created_at FROM decisions WHERE research_id=? AND decision='RELEASE_TO_C' ORDER BY created_at,id",(research_id,)).fetchall()
 prior=[{"id":r[0],"candidate_id":r[1],"created_at":r[3]} for r in rows]
 distinct={r[1] for r in rows}
 if candidate_id in distinct:failures.append("T09_CANDIDATE_ALREADY_RELEASED")
 if len(distinct)>=3:failures.append("T09_COMMISSION_LIMIT")
 if len(rows)!=len(distinct):failures.append("T09_DUPLICATE_HISTORY_REQUIRES_RECONCILIATION")
 evidence_dir=Path(evidence_dir)
 names={
  "T04":"w6_live_input_readiness.json",
  "T05":"w10_c_dependency_static_result.json",
  "T09":"w6_t09_commission_ledger_result.json",
  "T10":"w6_t10_policy_change_result.json"}
 evidence={}
 for control,filename in names.items():
  p=evidence_dir/filename
  if not p.is_file():
   evidence[control]={"state":"MISSING"};failures.append(control+"_EVIDENCE_MISSING");continue
  raw=p.read_bytes()
  try:
   obj=json.loads(raw)
   state=obj.get("verdict") or obj.get("overall") or "NO_VERDICT"
   evidence[control]={"state":state,"sha256":hashlib.sha256(raw).hexdigest(),"evidence_class":obj.get("evidence_class")}
  except (ValueError,TypeError):
   evidence[control]={"state":"INVALID_JSON"};failures.append(control+"_INVALID_EVIDENCE")
  # These are historical/read-only or synthetic records, not live verified authority.
  failures.append(control+"_LIVE_VERIFICATION_NOT_ESTABLISHED")
 # T04's resource contracts and T05's runtime inventory are not certified by the cited artifacts.
 # T10 change authority remains unbound to a trusted active decision register.
 failures.append("ACTIVE_RELEASE_AUTHORITY_NOT_ESTABLISHED")
 return {"state":"GOVERNANCE_HOLD","release_authorized":False,"candidate_id":candidate_id,
  "version":version,"research_id":research_id,"failures":sorted(set(failures)),
  "prior_releases":prior,"evidence":evidence}
