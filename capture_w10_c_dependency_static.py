"""Capture W10 C-stage dependency static tests with source provenance.
No orchestrator execution, API calls, or strategy execution.
"""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"Gate2_Evidence"/"Journal10_Dependency_Policy_FINAL"/"J10-E4_Revised_Policy"/"c_orchestrator_v3.py"
TEST=ROOT/"test_w10_c_dependency_static.py"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w10_c_dependency_static_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not SOURCE.is_file():raise SystemExit("Original W10 source missing")
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 p=subprocess.run([sys.executable,"-m","unittest","test_w10_c_dependency_static","-v"],cwd=ROOT,text=True,capture_output=True)
 log=p.stdout+"\n"+p.stderr
 cases=re.findall(r"^(test_T05_[ABC]_[^ ]+) \([^\n]+\) \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$",log,re.M)
 valid=(p.returncode==0 and len(cases)==3 and {n.split("_")[2] for n,_ in cases}=={"A","B","C"} and all(s=="ok" for _,s in cases) and re.search(r"Ran 3 tests? in",log) and re.search(r"^OK$",log,re.M))
 if not valid:raise SystemExit("Expected three PASS outcomes not reproduced; no evidence written")
 obj={"evidence_class":"W10_C_STAGE_STATIC_DEPENDENCY_TEST",
 "scope":"Actual W10 c_orchestrator_v3.static() function extracted by AST; no C orchestration or B-to-C integration executed",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_branch":branch,"git_commit":commit,
 "source_path":"Gate2_Evidence/Journal10_Dependency_Policy_FINAL/J10-E4_Revised_Policy/c_orchestrator_v3.py",
 "source_sha256":sha(SOURCE),"test_sha256":sha(TEST),
 "n":3,"denominator":3,"verdict":"PASS",
 "test_cases":[{"name":n,"result":s} for n,s in cases],
 "raw_log_sha256":hashlib.sha256(log.encode()).hexdigest(),
 "sanitized_log":"\n".join([f"{n} ... {s}" for n,s in cases]+["Ran 3 tests","OK"])+"\n",
 "production_authority":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Evidence exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Evidence written:",OUT.relative_to(ROOT))
if __name__=="__main__":main()
