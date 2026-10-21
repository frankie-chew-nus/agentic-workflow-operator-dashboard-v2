"""Fast-track Gate 2 regression runner. Local-only; preserves raw logs outside Git.

Runs existing governance suites in one pass, captures PASS/FAIL/SKIP and hashes.
Negative baseline tests are excluded deliberately and remain preserved separately.
Does not invoke real B adapter, strategy, AI API, or production DB.
"""
import datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
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
 "test_w10_c_dependency_static",
 "test_w10_c_dependency_hold",
]
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_fasttrack_regression.json"
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def main():
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 command=[sys.executable,"-m","unittest",*MODULES,"-v"]
 run=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
 log=run.stdout+"\n"+run.stderr
 # Store a sanitized summary; raw output is printed locally for inspection.
 import re
 found=re.findall(r"^([^\n]+) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 counts={k:sum(1 for _,s in found if s==k) for k in ("ok","FAIL","ERROR")}
 skipped=sum(1 for _,s in found if s.startswith("skipped"))
 tests_run=re.search(r"Ran (\d+) tests? in",log)
 result={"evidence_class":"B_GOVERNANCE_FASTTRACK_REGRESSION",
  "scope":"Selected positive experimental governance suites; NOT full historical T01-T10 or active production B-to-C verification",
  "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "git_branch":branch,"git_commit":commit,"modules":MODULES,
  "test_count_reported":int(tests_run.group(1)) if tests_run else None,
  "passed":counts["ok"],"failed":counts["FAIL"],"errors":counts["ERROR"],"skipped":skipped,
  "return_code":run.returncode,
  "verdict":"PASS" if run.returncode==0 and skipped==0 and tests_run and len(found)==int(tests_run.group(1)) else "NOT_FULLY_PASSING",
  "source_sha256":{p.name:sha(p) for p in [ROOT/(m+".py") for m in MODULES] if p.exists()},
  "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
  "production_authority":False,
  "limitations":["No authenticated Human approvals or authoritative production inventories",
                 "No active adapter modifications",
                 "Original negative baseline results remain separate"]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(log)
 print("Evidence written:",OUT.relative_to(ROOT))
 print("Verdict:",result["verdict"])
 if run.returncode:raise SystemExit(run.returncode)
if __name__=="__main__":main()
