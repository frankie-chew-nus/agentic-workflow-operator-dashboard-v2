"""Capture T09/T10 transition-guard negative findings, preserving honest scope."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TEST=ROOT/"test_w6_t09_t10_enforcement.py"
GUARD=ROOT/"workflow_matrix.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_t09_t10_findings.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="test/w6-governance-scenarios":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_w6_t09_t10_enforcement","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T(?:09|10)_[^ ]+) \([^\n]+\) \.\.\. (FAIL|ERROR|ok|skipped[^\n]*)$",log,re.M)
 valid=(p.returncode!=0 and len(cases)==2 and {x[0].split("_")[1] for x in cases}=={"T09","T10"} and all(x[1]=="FAIL" for x in cases) and "FAILED (failures=2)" in log and "T09 GAP:" in log and "T10 GAP:" in log)
 if not valid:raise SystemExit("Expected failures not reproduced; no evidence generated")
 obj={"evidence_class":"TRANSITION_GUARD_NEGATIVE_TEST","scope":"workflow_matrix.allowed only; scenario attributes not passed to guard; not full B-to-C workflow validation",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,"guard_sha256":sha(GUARD),"test_sha256":sha(TEST),
 "n":2,"denominator":2,"verdict":"COVERAGE_GAPS_CONFIRMED","failed":2,
 "findings":[{"id":"T09","observed":"AUTHORIZED without commission release count input","status":"GUARD_COVERAGE_GAP"},
 {"id":"T10","observed":"AUTHORIZED without actor or rule-change provenance input","status":"GUARD_COVERAGE_GAP"}],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{name} ... {status}" for name,status in cases]+["Ran 2 tests","FAILED (failures=2)"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
