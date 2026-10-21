"""Project-local HOLD-only dashboard deployment candidate, never activates."""
import argparse,hashlib,json,subprocess,sys,datetime,shutil
from pathlib import Path
from build_b_hold_only_dashboard import build
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--project-root",required=True);a=p.parse_args()
 project=Path(a.project_root).resolve(strict=True)
 if ROOT.parent!=project:raise SystemExit("PROJECT_ROOT_MISMATCH")
 source=ROOT/"gate2.py";before=hashlib.sha256(source.read_bytes()).hexdigest()
 run=project/"Test_Results"/("B_HOLD_Deployment_"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
 dest=run/"w6_disposable_dashboard";dest.mkdir(parents=True,exist_ok=False)
 for name in ("operator_artifacts.py","operator_paths.json"):
  shutil.copy2(ROOT/name,dest/name)
 build(source,dest/"gate2.py")
 test=subprocess.run([sys.executable,"-m","unittest","test_b_hold_only_dashboard_http",
  "test_local_pin_dashboard_http","test_b_local_operator_release","-v"],cwd=ROOT,capture_output=True,text=True,timeout=120)
 (run/"tests.txt").write_text(test.stdout+"\n"+test.stderr,encoding="utf-8")
 result={"status":"HOLD_ONLY_CANDIDATE_NOT_ACTIVATED",
  "candidate":str(dest/"gate2.py"),"tests_pass":test.returncode==0,
  "active_dashboard_unchanged":hashlib.sha256(source.read_bytes()).hexdigest()==before,
  "release_to_c":"UNCONDITIONALLY_BLOCKED","candidate_db_isolated":True,
  "governance_T04_T05_T09_T10":"HOLD","activation_authorized":False,
  "note":"No existing active candidate state or historical decision modified."}
 (run/"acceptance.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2))
 if test.returncode or not result["active_dashboard_unchanged"]:raise SystemExit(1)
if __name__=="__main__":main()
