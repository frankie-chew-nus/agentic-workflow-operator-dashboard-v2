"""E commissioning sandbox: audit workflow-test D evidence and fail closed."""
import json
from pathlib import Path
from operator_handoff import TEST,validate
def audit(d_handoff,required_decisions,observed_decisions,out_path):
 checks={}
 v=validate(d_handoff,"D",d_handoff.get("candidate_id"),d_handoff.get("version"),allow_test=True)
 checks["d_handoff_valid"]=v["pass"]
 checks["test_fixture_detected"]=d_handoff.get("evidence_kind")==TEST
 checks["required_human_decisions_present"]=all(x in observed_decisions for x in required_decisions)
 # Sandbox success means E correctly detects non-production provenance and blocks commissioning.
 blocked=checks["d_handoff_valid"] and checks["test_fixture_detected"]
 state="E_COMMISSIONING_BLOCKED_TEST_ARTIFACT" if blocked else "E_SANDBOX_HOLD"
 out={"state":state,"mode":"WORKFLOW_TEST_SANDBOX","candidate_id":d_handoff.get("candidate_id"),
      "checks":checks,"commissioning_authority":False,"commissioned":False,
      "advance_to_live":False,
      "warning":"WORKFLOW TEST EVIDENCE ONLY — NEVER COMMISSIONABLE"}
 Path(out_path).write_text(json.dumps(out,indent=2),encoding="utf-8");return out
