"""Capture seven isolated B preflight test outcomes as sanitized Gate 2 evidence.

Does not access production databases, strategy code, or live workflow.
"""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_isolated_b_preflight_result.json"
FILES=("b_boundary_policy_v1.py","isolated_b_preflight_adapter.py","test_isolated_b_preflight_adapter.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_isolated_b_preflight_adapter","-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 if p.returncode!=0 or len(cases)!=7 or any(s!="ok" for _,s in cases) or not re.search(r"Ran 7 tests? in",log) or not re.search(r"^OK$",log,re.M):
  raise SystemExit("Expected seven PASS outcomes not reproduced; no evidence written")
 obj={"evidence_class":"ISOLATED_B_PREFLIGHT_SYNTHETIC_TEST",
 "scope":"Synthetic policy context; NOT integrated with active B workflow or production authority",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,
 "source_sha256":{f:sha(ROOT/f) for f in FILES},
 "n":7,"denominator":7,"verdict":"PASS",
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 7 tests","OK"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
