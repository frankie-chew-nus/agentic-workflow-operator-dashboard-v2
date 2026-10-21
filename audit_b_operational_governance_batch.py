"""One-pass operational governance audit for the local MSI5002 dashboard.

Read-only: never changes candidate states, approval manifest, PIN config or
production dashboard. Evaluates operational evidence separately from policies.
Output stays under 5002/Gate2_Evidence.
"""
import argparse,datetime,hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
POLICIES={"T04":"T04_OPERATOR_POLICY_APPROVAL_2026-10-21.md",
"T05":"T05_OPERATOR_POLICY_APPROVAL_2026-10-21.md",
"T09":"T09_DISTINCT_CANDIDATE_COUNTING_APPROVAL_2026-10-21.md",
"T10":"T09_T10_OPERATOR_POLICY_APPROVAL_2026-10-21.md"}
ARTIFACTS={
"T04":["w6_live_input_readiness.json","w6_active_b_t04_t05_t09_t10_findings.json"],
"T05":["w10_c_dependency_static_result.json","w10_c_dependency_hold_routing_result.json","w6_active_b_t04_t05_t09_t10_findings.json"],
"T09":["w6_t09_commission_ledger_result.json","T09_C002_RELEASE_RECONCILIATION_PENDING.md","w6_t09_t10_findings.json"],
"T10":["w6_t10_policy_change_result.json","w6_t09_t10_findings.json"]}
def fileinfo(path):
 return {"present":path.is_file(),"path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None}
def audit(evidence,db):
 evidence=Path(evidence).resolve();db=Path(db).resolve()
 controls={}
 for key in POLICIES:
  controls[key]={"policy":fileinfo(evidence/POLICIES[key]),
   "operational_artifacts":[fileinfo(evidence/name) for name in ARTIFACTS[key]],
   "verdict":"HOLD_PENDING_CONTENT_AND_AUTHORITY_REVIEW"}
 rows=[];candidates=[];issues=[]
 if db.is_file():
  conn=sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)
  try:
   rows=[dict(zip(("id","research_id","candidate_id","decision","rationale","created_at"),row))
    for row in conn.execute("SELECT id,research_id,candidate_id,decision,rationale,created_at FROM decisions ORDER BY created_at")]
   candidates=[dict(zip(("id","research_id","state","version"),row))
    for row in conn.execute("SELECT id,research_id,state,version FROM candidates ORDER BY id")]
  finally:conn.close()
 else:issues.append("DASHBOARD_DB_MISSING")
 releases=[r for r in rows if r["decision"]=="RELEASE_TO_C"]
 if any(r["candidate_id"]=="CAND-B-002" for r in releases):
  issues.append("CAND_B_002_ALREADY_RELEASED_DO_NOT_REISSUE")
 if any(c["id"]=="CAND-B-002" and c["state"]!="B_REVIEW" for c in candidates):
  issues.append("CAND_B_002_NOT_IN_B_REVIEW")
 if not all(x["policy"]["present"] for x in controls.values()):issues.append("POLICY_DOCUMENT_MISSING")
 if not all(all(y["present"] for y in x["operational_artifacts"]) for x in controls.values()):
  issues.append("OPERATIONAL_ARTIFACT_MISSING")
 return {"status":"HOLD_RECONCILIATION_REQUIRED","generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "controls":controls,"dashboard_releases":releases,"candidate_states":candidates,
 "issues":issues,"operator_approval_recorded":False,"activation_authorized":False,
 "active_files_modified":False,"next_actions":[
 "Read operational artifact contents; distinguish policy approvals from actual verification",
 "Reconcile CAND-B-002 historical release across dashboard and B workflow ledgers",
 "Do not re-release existing C-stage candidates",
 "Only after verified evidence and explicit approval, prepare guarded activation"]}
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--project-root",required=True)
 a=p.parse_args();root=Path(a.project_root).resolve(strict=True)
 if ROOT.parent!=root:raise SystemExit("PROJECT_ROOT_MISMATCH")
 evidence=ROOT/"gate2_submission_evidence"/"governance_tests"
 result=audit(evidence,ROOT/"evidence"/"operator.db")
 dest=root/"Gate2_Evidence"/"B_GOVERNANCE_OPERATIONAL_AUDIT.json"
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():raise SystemExit("EXISTING_AUDIT_REFUSE_OVERWRITE")
 dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Audit:",dest)
 print("Historical releases:",len(result["dashboard_releases"]))
 print("Issues:",", ".join(result["issues"]) or "none")
 print("Status:",result["status"])
