"""Dashboard-safe D sandbox demo adapter. Never reads or mutates real C evidence."""
import json
from pathlib import Path
from operator_handoff import TEST,envelope
from d_sandbox import run
def execute(root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True)
 c=root/"c_test_fixture.json";c.write_text(json.dumps({"state":"C_TEST_FIXTURE","purpose":"D_WORKFLOW_DEVELOPMENT_ONLY"},indent=2))
 h=envelope("C","FIX-D-001","v0",TEST,[("c_test_fixture",c)],"C_TEST_FIXTURE")
 (root/"c_test_handoff.json").write_text(json.dumps(h,indent=2))
 hidden=[{"t":1,"outcome":1},{"t":2,"outcome":-1},{"t":3,"outcome":1}]
 result=run(h,hidden,root/"d_output")
 summary={"state":result["state"],"mode":"WORKFLOW_TEST_SANDBOX","candidate_id":"FIX-D-001",
          "production_authority":False,"advance_to_e_production":False,
          "warning":"TEST FIXTURE ONLY — NOT A C PASS — NOT TRADING EVIDENCE — NOT COMMISSIONING AUTHORITY",
          "d_result":result}
 (root/"dashboard_summary.json").write_text(json.dumps(summary,indent=2))
 return summary
