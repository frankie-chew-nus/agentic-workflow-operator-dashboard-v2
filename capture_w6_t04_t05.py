"""Capture reproducible W6 T04/T05 failures as negative governance evidence."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHECKER=ROOT.parent/"gate2_build_v03B2"/"b_v2.py"
TEST=ROOT/"test_w6_t04_t05_enforcement.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_t04_t05_findings.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not CHECKER.is_file():raise SystemExit("Historical checker missing")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="test/w6-governance-scenarios":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_w6_t04_t05_enforcement","-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T0[45]_[^ ]+) \([^\n]+\) \.\.\. (FAIL|ERROR|ok|skipped[^\n]*)$",log,re.M)
 expected=(len(cases)==2 and {x[0].split("_")[1] for x in cases}=={"T04","T05"} and all(x[1]=="FAIL" for x in cases) and "FAILED (failures=2)" in log and "T04 GAP:" in log and "T05 GAP:" in log and p.returncode!=0)
 if not expected:raise SystemExit("Expected two enforcement failures not reproduced; no evidence written")
 result={"evidence_class":"HISTORICAL_B_CHECKER_NEGATIVE_EXECUTABLE_TEST",
 "scope":"Historical b_v2.checks only; current B-to-C production enforcement NOT VERIFIED",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,"checker_path":"../gate2_build_v03B2/b_v2.py",
 "checker_sha256":sha(CHECKER),"test_file_sha256":sha(TEST),
 "n":2,"denominator":2,"verdict":"ENFORCEMENT_GAPS_FOUND","passed":0,"failed":2,
 "findings":[{"id":"T04","expected":"HOLD","observed":"No validation failures for unavailable resource","status":"FAIL"},
 {"id":"T05","expected":"HOLD","observed":"No validation failures for opaque dependency","status":"FAIL"}],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{name} ... {state}" for name,state in cases]+["Ran 2 tests","FAILED (failures=2)"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
