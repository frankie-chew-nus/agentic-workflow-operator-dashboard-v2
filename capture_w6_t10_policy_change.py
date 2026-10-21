"""Capture T10 synthetic policy-change tests with reproducible provenance."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_t10_policy_change_result.json"
FILES=("b_policy_change_gate_v1.py","test_b_policy_change_gate_v1.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_b_policy_change_gate_v1","-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T10_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 valid=(p.returncode==0 and len(cases)==7 and len({n for n,_ in cases})==7 and
        all(s=="ok" for _,s in cases) and re.search(r"Ran 7 tests? in",log) and re.search(r"^OK$",log,re.M))
 if not valid:raise SystemExit("Seven PASS results not reproduced; no evidence written")
 obj={"evidence_class":"SYNTHETIC_T10_POLICY_CHANGE_TEST",
 "scope":"Experimental authorization gate; synthetic decisions, no authenticated Human approval or active workflow integration",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,
 "source_sha256":{f:sha(ROOT/f) for f in FILES},
 "n":7,"denominator":7,"verdict":"PASS",
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 7 tests","OK"])+"\n",
 "production_authority":False,
 "limitations":["Synthetic decision registry does not authenticate Human identity",
 "No integration with active B release boundary"]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
