"""Controlled B integration candidate (NOT installed in active workflow).

Runs a copied B adapter only after experimental consolidated preflight. Requires
explicit disposable fixture root and blocks all production use. Trusted inputs
are synthetic test-only; activation requires a separate design and Human approval.
"""
import json,subprocess,sys
from pathlib import Path
from consolidated_b_governance_preflight import evaluate

def run(candidate,context,*,fixture_root,adapter,db,register,corrected_candidate):
 root=Path(fixture_root).resolve()
 paths=[Path(p).resolve() for p in (adapter,db,register,corrected_candidate)]
 if root.name!="w6_disposable_fixture" or any(root not in p.parents for p in paths):
  return {"state":"GOVERNANCE_HOLD","reason":"NON_DISPOSABLE_PATH","adapter_executed":False}
 result=evaluate(candidate,context)
 if result["state"]!="PREFLIGHT_PASS_TEST_ONLY":
  return {"state":"GOVERNANCE_HOLD","failures":result["failures"],"adapter_executed":False}
 out=root/"output"
 cmd=[sys.executable,str(paths[0]),"--db",str(paths[1]),"--register",str(paths[2]),
      "--candidate",str(candidate["candidate_id"]),"--corrected-candidate",str(paths[3]),"--output-dir",str(out)]
 p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=20)
 return {"state":"B_RESUME_TEST_ONLY" if p.returncode==0 else "GOVERNANCE_HOLD",
         "return_code":p.returncode,"adapter_executed":True,"production_authority":False}
