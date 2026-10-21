"""Capture seven consolidated B preflight tests as sanitized Gate 2 evidence."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_consolidated_b_preflight_result.json"
FILES=("b_boundary_policy_v1.py","b_commission_release_ledger_v1.py",
       "b_policy_change_gate_v1.py","consolidated_b_governance_preflight.py",
       "test_consolidated_b_governance_preflight.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_consolidated_b_governance_preflight","-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 expected={"test_T04_missing_resource","test_T05_opaque_dependency","test_T09_fourth_candidate",
           "test_T10_unapproved_policy_change","test_missing_context_holds",
           "test_unverified_decisions_hold","test_valid_fixture_no_release_authority"}
 valid=(p.returncode==0 and len(cases)==7 and {n for n,_ in cases}==expected
        and all(s=="ok" for _,s in cases) and re.search(r"Ran 7 tests? in",log)
        and re.search(r"^OK$",log,re.M))
 if not valid:raise SystemExit("Expected seven PASS results not reproduced; no evidence written")
 obj={"evidence_class":"SYNTHETIC_CONSOLIDATED_B_PREFLIGHT_TEST",
 "scope":"Experimental consolidated gate with synthetic context; not connected to active B adapter",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,
 "source_sha256":{f:sha(ROOT/f) for f in FILES},
 "n":7,"denominator":7,"verdict":"PASS",
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 7 tests","OK"])+"\n",
 "production_authority":False,
 "limitations":["Trusted context is synthetic, not authenticated",
 "No active B-to-C integration or production authorization"]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
