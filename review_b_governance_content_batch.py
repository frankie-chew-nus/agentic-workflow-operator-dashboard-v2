"""Operational B governance evidence review in one pass, read-only.

Reads actual JSON artifact content and both existing decision databases, records
observed statuses without treating file presence as PASS. Outputs under 5002.
"""
import argparse,datetime,hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARTIFACTS={
"T04":["w6_live_input_readiness.json","w6_active_b_t04_t05_t09_t10_findings.json"],
"T05":["w10_c_dependency_static_result.json","w10_c_dependency_hold_routing_result.json","w6_active_b_t04_t05_t09_t10_findings.json"],
"T09":["w6_t09_commission_ledger_result.json","w6_t09_t10_findings.json"],
"T10":["w6_t10_policy_change_result.json","w6_t09_t10_findings.json"]}
def load_artifact(path):
 if not path.is_file():return {"status":"MISSING"}
 try:
  raw=path.read_bytes();obj=json.loads(raw)
  return {"status":"READ","sha256":hashlib.sha256(raw).hexdigest(),"content":obj}
 except (OSError,ValueError) as exc:return {"status":"UNREADABLE","error":type(exc).__name__}
def ledger(path):
 if not path.is_file():return {"status":"MISSING","releases":[]}
 c=sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)
 try:
  names={x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
  if "decisions" not in names:return {"status":"NO_DECISIONS_TABLE","releases":[]}
  columns={x[1] for x in c.execute("PRAGMA table_info(decisions)")}
  fields=[x for x in ("id","research_id","candidate_id","decision","rationale","created_at") if x in columns]
  if not {"candidate_id","decision"}.issubset(fields):return {"status":"INCOMPATIBLE_SCHEMA","releases":[]}
  q="SELECT "+",".join(fields)+" FROM decisions WHERE decision='RELEASE_TO_C'"
  return {"status":"READ","releases":[dict(zip(fields,row)) for row in c.execute(q)]}
 finally:c.close()
def main():
 p=argparse.ArgumentParser();p.add_argument("--project-root",required=True)
 p.add_argument("--workflow-db");a=p.parse_args()
 root=Path(a.project_root).resolve(strict=True)
 if root!=ROOT.parent:raise SystemExit("PROJECT_ROOT_MISMATCH")
 ev=ROOT/"gate2_submission_evidence"/"governance_tests"
 controls={key:{name:load_artifact(ev/name) for name in names} for key,names in ARTIFACTS.items()}
 dashboard=ledger(ROOT/"evidence"/"operator.db")
 workflow=ledger(Path(a.workflow_db).resolve()) if a.workflow_db else {"status":"NOT_SPECIFIED","releases":[]}
 a_releases=dashboard["releases"];b_releases=workflow["releases"]
 matches=[{"dashboard":d,"workflow":w} for d in a_releases for w in b_releases
          if d.get("candidate_id")==w.get("candidate_id") and d.get("research_id")==w.get("research_id")]
 result={"status":"CONTENT_REVIEW_REQUIRED_NO_ACTIVATION",
 "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "controls":controls,"dashboard_ledger":dashboard,"workflow_ledger":workflow,
 "cross_ledger_matches":matches,
 "unreconciled_dashboard_releases":[x for x in a_releases if not any(x.get("candidate_id")==m["dashboard"].get("candidate_id") and x.get("id")==m["dashboard"].get("id") for m in matches)],
 "notes":["Content is raw evidence, not independently verified PASS",
          "Cross-ledger candidate matching alone does not prove release provenance",
          "Never release CAND-B-002 again without new governed commission and state"],
 "manifest_modified":False,"database_modified":False,"activation_authorized":False}
 out=root/"Gate2_Evidence"/"B_GOVERNANCE_CONTENT_REVIEW.json"
 if out.exists():raise SystemExit("OUTPUT_EXISTS_REFUSE_OVERWRITE")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
 print("Saved:",out)
 print("Dashboard releases:",len(a_releases),"Workflow releases:",len(b_releases))
 print("Status:",result["status"])
if __name__=="__main__":main()
