"""Capture synthetic B provenance tests as sanitized Gate 2 evidence."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_b_policy_provenance_result.json"
FILES=("b_policy_provenance_v1.py","test_b_policy_provenance_v1.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_b_policy_provenance_v1","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 if p.returncode!=0 or len(cases)!=6 or any(s!="ok" for _,s in cases) or not re.search(r"Ran 6 tests? in",log) or not re.search(r"^OK$",log,re.M):
  raise SystemExit("Expected six PASS outcomes not reproduced; no evidence written")
 obj={"evidence_class":"SYNTHETIC_B_POLICY_PROVENANCE_TEST",
 "scope":"Structural and hash checks only; no Human authentication, trusted source of truth, or active workflow integration",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,"source_sha256":{f:sha(ROOT/f) for f in FILES},
 "n":6,"denominator":6,"verdict":"PASS",
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 6 tests","OK"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
