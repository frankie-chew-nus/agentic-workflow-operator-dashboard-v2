"""Capture verified disposable B integration tests as sanitized Gate 2 evidence.
No production databases, active adapters, or strategy execution are touched.
"""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"gate2_operator_app_v1"/"b_resume.py"
FILES=("b_boundary_policy_v1.py","isolated_b_preflight_adapter.py",
       "disposable_b_integration.py","test_disposable_b_integration.py")
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_disposable_b_integration_result.json"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def main():
 if not SOURCE.is_file():raise SystemExit("Original active B adapter not found")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 proc=subprocess.run([sys.executable,"-m","unittest","test_disposable_b_integration","-v"],
                     cwd=ROOT,capture_output=True,text=True)
 log=proc.stdout+"\n"+proc.stderr
 cases=re.findall(r"^(test_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 expected={"test_T04_blocks_before_adapter","test_T05_blocks_before_adapter",
           "test_T09_blocks_before_adapter","test_T10_blocks_before_adapter",
           "test_valid_fixture_reaches_copied_adapter_only"}
 valid=(proc.returncode==0 and len(cases)==5 and {name for name,_ in cases}==expected
        and all(status=="ok" for _,status in cases)
        and re.search(r"Ran 5 tests? in",log) and re.search(r"^OK$",log,re.M))
 if not valid:raise SystemExit("Five required PASS results not reproduced; evidence not written")
 obj={"evidence_class":"DISPOSABLE_B_ADAPTER_INTEGRATION_TEST",
      "scope":"Synthetic trusted context, temporary SQLite, copied b_resume.py; NOT active B workflow integration",
      "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "git_branch":branch,"git_commit":commit,
      "source_sha256":{f:sha(ROOT/f) for f in FILES},
      "copied_adapter_source_sha256":sha(SOURCE),
      "n":5,"denominator":5,"verdict":"PASS",
      "test_cases":[{"name":name,"result":status} for name,status in cases],
      "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
      "sanitized_log":"\n".join([f"{name} ... {status}" for name,status in cases]+["Ran 5 tests","OK"])+"\n",
      "production_authority":False,
      "remaining_limitations":["No authoritative live resource inventory or dependency allowlist",
       "No authoritative commission release count or rule-change approval",
       "No active adapter modification or complete B-to-C end-to-end test"]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence already exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
