"""Capture active B resume T04/T05/T09/T10 negative findings.
Requires local ../gate2_operator_app_v1/b_resume.py. No production changes.
"""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ADAPTER=ROOT.parent/"gate2_operator_app_v1"/"b_resume.py"
TEST=ROOT/"test_w6_active_b_governance.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_active_b_t04_t05_t09_t10_findings.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not ADAPTER.is_file():raise SystemExit("Active adapter absent; no evidence written")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="test/w6-governance-scenarios":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_w6_active_b_governance","-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T(?:04|05|09|10)_[^ ]+) \([^\n]+\) \.\.\. (FAIL|ERROR|ok|skipped[^\n]*)$",log,re.M)
 valid=(p.returncode!=0 and len(cases)==4 and {n.split("_")[1] for n,_ in cases}=={"T04","T05","T09","T10"} and all(s=="FAIL" for _,s in cases) and "FAILED (failures=4)" in log and all(f"{x}: expected governance HOLD" in log for x in ("T04","T05","T09","T10")))
 if not valid:raise SystemExit("Expected four negative findings not reproduced; no evidence written")
 obj={"evidence_class":"ACTIVE_B_RESUME_NEGATIVE_INTEGRATION_TEST",
 "scope":"b_resume.py with disposable SQLite DB and synthetic candidate; tests are NOT full B-to-C release path",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,"adapter_path":"../gate2_operator_app_v1/b_resume.py",
 "adapter_sha256":sha(ADAPTER),"test_sha256":sha(TEST),
 "n":4,"denominator":4,"test_run_verdict":"FAILED_EXPECTED_GAPS","passed":0,"failed":4,
 "findings":[{"id":t,"expected":"GOVERNANCE_HOLD (exit 2)","observed":"b_resume.py returned 0 (candidate awaiting Human release)","status":"BOUNDARY_GAP"} for t in ("T04","T05","T09","T10")],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{name} ... {status}" for name,status in cases]+["Ran 4 tests","FAILED (failures=4)"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
