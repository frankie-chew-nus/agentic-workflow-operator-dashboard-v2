"""Final experimental B governance regression and one sanitized evidence record.

Runs existing positive suites plus controlled disposable integration. Deliberately
excludes historical expected-failure baselines (preserved separately). Does not
activate B production governance or access production SQLite.
"""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_final_experimental_regression.json"
MODULES=[
 "test_b_boundary_policy_v1",
 "test_isolated_b_policy_harness",
 "test_isolated_b_preflight_adapter",
 "test_b_governance_policy_schema",
 "test_b_policy_provenance_v1",
 "test_b_commission_release_ledger_v1",
 "test_b_policy_change_gate_v1",
 "test_consolidated_b_governance_preflight",
 "test_disposable_b_integration",
 "test_controlled_b_integration_candidate",
 "test_w10_c_dependency_static",
 "test_w10_c_dependency_hold",
]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest",*MODULES,"-v"],cwd=ROOT,capture_output=True,text=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^([^\n]+) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 ran=re.search(r"Ran (\d+) tests? in",log)
 count=int(ran.group(1)) if ran else None
 passed=sum(s=="ok" for _,s in cases)
 skipped=sum(s.startswith("skipped") for _,s in cases)
 failures=sum(s=="FAIL" for _,s in cases)
 errors=sum(s=="ERROR" for _,s in cases)
 valid=(p.returncode==0 and count is not None and count>=74 and len(cases)==count and passed==count and skipped==0 and failures==0 and errors==0 and re.search(r"^OK$",log,re.M))
 result={"evidence_class":"FINAL_EXPERIMENTAL_B_GOVERNANCE_REGRESSION",
  "scope":"Selected synthetic and disposable B/C checks only; NOT active production B-to-C enforcement or full T01-T10 certification",
  "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "git_branch":branch,"git_commit":commit,"modules":MODULES,
  "tests_run":count,"passed":passed,"failed":failures,"errors":errors,"skipped":skipped,
  "verdict":"PASS" if valid else "NOT_FULLY_PASSING",
  "source_sha256":{m+".py":sha(ROOT/(m+".py")) for m in MODULES},
  "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
  "sanitized_log":"\n".join(f"{n} ... {s}" for n,s in cases)+f"\nRan {count} tests\n"+("OK" if valid else "NOT_FULLY_PASSING")+"\n",
  "production_authority":False,
  "limitations":["Human approval and resource inventories not authenticated",
   "Original historical negative tests retained separately",
   "Active B adapter and D/E authority unchanged"]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(log)
 print("Evidence written:",OUT.relative_to(ROOT))
 print("Verdict:",result["verdict"],"Tests:",count)
 if not valid:raise SystemExit(1)
if __name__=="__main__":main()
