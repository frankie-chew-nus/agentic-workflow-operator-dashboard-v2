"""One-shot A-E acceptance: existing tests, local audit report, no active DB writes.

Reports to 5002/Gate2_Evidence; does not create a Portfolio or touch PIN.
"""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES=("test_ae_build_contract","test_b_operational_boundary",
        "test_actual_dashboard_hold_no_pin","test_local_pin_dashboard_http")
# The legacy local PIN dashboard test is intentionally excluded from this
# acceptance run because PIN is no longer part of the actual build.
SUITES=SUITES[:-1]
def main():
 p=argparse.ArgumentParser();p.add_argument("--project-root",required=True)
 a=p.parse_args();project=Path(a.project_root).resolve(strict=True)
 if project!=ROOT.parent:raise SystemExit("PROJECT_ROOT_MISMATCH")
 source=ROOT/"gate2.py";before=hashlib.sha256(source.read_bytes()).hexdigest()
 result=subprocess.run([sys.executable,"-m","unittest",*SUITES,"-v"],
  cwd=ROOT,capture_output=True,text=True,timeout=180)
 after=hashlib.sha256(source.read_bytes()).hexdigest()
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
 out=project/"Gate2_Evidence"/"AE_Acceptance"/stamp
 out.mkdir(parents=True,exist_ok=False)
 (out/"unittest.txt").write_text(result.stdout+"\n"+result.stderr,encoding="utf-8")
 report={"status":"PASS" if result.returncode==0 and before==after else "FAIL",
  "test_exit_code":result.returncode,"suites":list(SUITES),
  "active_dashboard_unchanged":before==after,"active_dashboard_sha256":after,
  "B_to_C_release":"HOLD_ONLY","C_stage":"REVIEW_REQUIRED",
  "D_E":"SANDBOX_ONLY","T04_T05_T09_T10":"OPERATIONAL_HOLD",
  "pin_in_scope":False,"production_authority":False,
  "limitations":["No live release authorization","No independent historical B ledger reconciliation",
                 "No C_PASS or D_OOS_PASS proven for current candidate"],
  "git_evidence_record":"gate2_evidence/AE_BUILD_STATUS_2026-10-21.md"}
 (out/"acceptance.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
 print("Evidence directory:",out)
 if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
