"""Capture sanitized W6 T01-T03 executable evidence locally; no API calls."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHECKER=ROOT.parent/"gate2_build_v03B2"/"b_v2.py"
TEST=ROOT/"test_w6_historical_b_executable.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_t01_t03_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not CHECKER.is_file():raise SystemExit("Checker missing; no evidence produced")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="test/w6-governance-scenarios":raise SystemExit("Wrong branch")
 p=subprocess.run([sys.executable,"-m","unittest","test_w6_historical_b_executable","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 names=re.findall(r"^(test_T0[123]_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 success=(p.returncode==0 and len(names)==3 and {x[0].split("_")[1] for x in names}=={"T01","T02","T03"} and all(x[1]=="ok" for x in names) and re.search(r"Ran 3 tests? in",log) and re.search(r"^OK$",log,re.M))
 if not success:raise SystemExit("Required 3 executed PASS results not confirmed; no evidence produced")
 result={"evidence_class":"HISTORICAL_B_CHECKER_EXECUTABLE_TEST",
 "scope":"T01-T03 candidate checks only; not end-to-end current B-to-C enforcement",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_commit":commit,"git_branch":branch,"checker_path":"../gate2_build_v03B2/b_v2.py",
 "checker_sha256":sha(CHECKER),"test_file_sha256":sha(TEST),
 "test_cases":[{"name":name,"result":state} for name,state in names],
 "n":3,"denominator":3,"verdict":"PASS","production_authority":False,
 "log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{name} ... {state}" for name,state in names]+["Ran 3 tests","OK"])+"\n"}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
