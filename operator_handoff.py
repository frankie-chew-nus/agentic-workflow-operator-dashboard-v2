"""Typed evidence contracts for safe Operator stage handoffs."""
import hashlib,json
from pathlib import Path
PRODUCTION="PRODUCTION_EVIDENCE"
TEST="WORKFLOW_TEST_FIXTURE"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def envelope(stage,candidate_id,version,kind,artifacts,state):
 if kind not in (PRODUCTION,TEST):raise ValueError("invalid evidence kind")
 return {"schema":"operator-handoff-v1","stage":stage,"candidate_id":candidate_id,"version":version,
         "evidence_kind":kind,"state":state,"artifacts":[{"role":r,"path":str(p),"sha256":sha(p)} for r,p in artifacts]}
def validate(e,expected_stage,candidate_id,version,allow_test=False):
 checks={"schema":e.get("schema")=="operator-handoff-v1","stage":e.get("stage")==expected_stage,
 "candidate":e.get("candidate_id")==candidate_id,"version":e.get("version")==version,
 "kind":e.get("evidence_kind") in ((PRODUCTION,TEST) if allow_test else (PRODUCTION,))}
 for a in e.get("artifacts",[]):
  p=Path(a.get("path",""));checks["artifact:"+a.get("role","?")]=p.is_file() and sha(p)==a.get("sha256")
 return {"pass":all(checks.values()),"checks":checks}
