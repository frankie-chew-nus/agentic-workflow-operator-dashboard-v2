"""Disposable B-boundary integration: preflight before existing b_resume subprocess.

TEST ONLY: synthetic trusted context; no active DB or source changes.
Refuses any adapter path outside the local copied test fixture.
"""
import json,subprocess,sys
from pathlib import Path
from isolated_b_preflight_adapter import preflight

def run_disposable(candidate,context,*,adapter,db,register,output_dir,corrected_candidate):
    paths=[Path(x).resolve() for x in (adapter,db,register,output_dir,corrected_candidate)]
    adapter,db,register,output_dir,corrected_candidate=paths
    # Require ALL paths under one explicit disposable root; never follow real workflow paths.
    root=output_dir.parent
    if root.name!="w6_disposable_fixture":
        return {"state":"GOVERNANCE_HOLD","reason":"NOT_DISPOSABLE_ROOT"}
    if any(root not in p.parents and p!=root for p in paths):
        return {"state":"GOVERNANCE_HOLD","reason":"PATH_OUTSIDE_FIXTURE"}
    result=preflight(candidate,context)
    if result["state"]!="PREFLIGHT_PASS_TEST_ONLY":
        return {"state":"GOVERNANCE_HOLD","failures":result["failures"],"adapter_executed":False}
    cmd=[sys.executable,str(adapter),"--db",str(db),"--register",str(register),
         "--candidate",candidate["candidate_id"],"--corrected-candidate",str(corrected_candidate),
         "--output-dir",str(output_dir)]
    proc=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=15)
    return {"state":"B_RESUME_TEST_ONLY" if proc.returncode==0 else "B_RESUME_HOLD",
            "return_code":proc.returncode,"adapter_executed":True,"production_authority":False}
