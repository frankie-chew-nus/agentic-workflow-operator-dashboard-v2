"""Capture sanitized isolated B policy test evidence. No production access."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_isolated_remediation_result.json"
FILES=("b_boundary_policy_v1.py","isolated_b_policy_harness.py","test_isolated_b_policy_harness.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_isolated_b_policy_harness","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 valid=(p.returncode==0 and len(cases)==6 and all(s=="ok" for _,s in cases) and re.search(r"Ran 6 tests? in",log) and re.search(r"^OK$",log,re.M))
 if not valid:raise SystemExit("Six passing tests not reproduced; no evidence written")
 obj={"evidence_class":"ISOLATED_POLICY_REMEDIATION_TEST",
 "scope":"Synthetic policy/harness tests only; active B adapter not modified or integrated",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,
 "source_sha256":{f:sha(ROOT/f) for f in FILES},
 "n":6,"denominator":6,"verdict":"PASS","production_authority":False,
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 6 tests","OK"])+"\n"}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
