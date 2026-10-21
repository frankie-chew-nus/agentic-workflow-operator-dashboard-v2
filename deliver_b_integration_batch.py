"""Batch B->C integration delivery, project-local and fail closed.

Produces an isolated runnable dashboard package under 5002, performs local
governance reconciliation, and runs the existing integration regression.
Never modifies active gate2.py or active databases, never enables release.
"""
import argparse,hashlib,json,shutil,subprocess,sys,datetime
from pathlib import Path
from build_local_pin_dashboard_candidate import build
from b_local_operator_release import check_evidence
ROOT=Path(__file__).resolve().parent
REQUIRED=("gate2.py","operator_artifacts.py","operator_paths.json",
          "b_local_operator_release.py","b_disposable_pin_authority.py")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project-root",required=True)
 a=p.parse_args();project=Path(a.project_root).resolve(strict=True)
 if ROOT.parent!=project:raise SystemExit("PROJECT_ROOT_MISMATCH")
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
 out=project/"Test_Results"/("B_Integration_"+stamp)
 if out.exists():raise SystemExit("OUTPUT_EXISTS")
 target=out/"w6_disposable_dashboard";target.mkdir(parents=True)
 missing=[name for name in REQUIRED if not (ROOT/name).is_file()]
 if missing:raise SystemExit("REQUIRED_SOURCE_MISSING:"+",".join(missing))
 before=hashlib.sha256((ROOT/"gate2.py").read_bytes()).hexdigest()
 for name in REQUIRED:
  if name!="gate2.py":shutil.copy2(ROOT/name,target/name)
 build(ROOT/"gate2.py",target/"gate2.py")
 # Test-only local config: never copy PIN hash into a distributable package.
 cfg=project/"Local_Approval"/"local_approval_config.json"
 evidence="CONFIG_MISSING";enabled=False
 if cfg.exists():
  try:
   c=json.loads(cfg.read_text(encoding="utf-8"))
   mpath=Path(c["evidence_manifest"])
   m=json.loads(mpath.read_text(encoding="utf-8"))
   evidence=check_evidence(m.get("candidate_id"),m.get("candidate_version"),m.get("research_id"),mpath) or "PASS"
   enabled=c.get("enabled") is True
  except Exception as exc:evidence="INVALID_CONFIG:"+type(exc).__name__
 tests=("test_b_local_operator_release","test_build_local_pin_dashboard_candidate",
        "test_local_pin_dashboard_http","test_b_disposable_pin_atomic")
 proc=subprocess.run([sys.executable,"-m","unittest",*tests,"-v"],cwd=ROOT,
                     capture_output=True,text=True,timeout=120)
 (out/"regression.txt").write_text(proc.stdout+"\n"+proc.stderr,encoding="utf-8")
 after=hashlib.sha256((ROOT/"gate2.py").read_bytes()).hexdigest()
 result={"status":"REVIEW_ONLY_NO_ACTIVATION","project_root":str(project),
  "candidate":str(target/"gate2.py"),"test_exit_code":proc.returncode,
  "governance_evidence":evidence,"release_enabled":enabled,
  "active_dashboard_unchanged":before==after,"active_dashboard_sha256":after,
  "production_authority":False,"candidate_uses_local_config_env":"GATE2_LOCAL_APPROVAL_CONFIG",
  "candidate_database":"isolated copy must be initialized separately; never point at active DB",
  "activation_authorized":False,
  "remaining":["Review T04/T05 operational evidence","Reconcile historical T09 release",
               "Verify T10 decision register","Approve guarded activation separately"]}
 (out/"integration_report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2))
 if proc.returncode or before!=after:raise SystemExit(1)
if __name__=="__main__":main()
