"""Capture W6 T06-T10 transition tests with honest scenario coverage labels."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TEST=ROOT/"test_w6_t06_t10_transition.py"
GUARD=ROOT/"workflow_matrix.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_t06_t10_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="test/w6-governance-scenarios":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_w6_t06_t10_transition","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T(?:06|07|08|09|10)_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 ids={name.split("_")[1] for name,_ in cases}
 if p.returncode or len(cases)!=5 or ids!={"T06","T07","T08","T09","T10"} or any(status!="ok" for _,status in cases) or not re.search(r"Ran 5 tests? in",log) or not re.search(r"^OK$",log,re.M):
  raise SystemExit("Expected five passing tests not verified; no evidence written")
 result={"evidence_class":"EXECUTABLE_TRANSITION_GUARD_TEST","scope":"workflow_matrix.allowed only; not full W6.2 B-to-C enforcement",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,"test_sha256":sha(TEST),"guard_sha256":sha(GUARD),
 "n":5,"denominator":5,"test_run_verdict":"PASS",
 "scenario_assessment":{"T06":"PARTIAL: human flag hold","T07":"PARTIAL: repeated human=false; no real time/reminder test",
 "T08":"PARTIAL: identity/hash holds; no version-retention test",
 "T09":"NOT_VERIFIED: aggregate-limit enforcement not tested",
 "T10":"NOT_VERIFIED: rule-change authority not tested"},
 "test_cases":[{"name":name,"result":status} for name,status in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{name} ... {status}" for name,status in cases]+["Ran 5 tests","OK"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
