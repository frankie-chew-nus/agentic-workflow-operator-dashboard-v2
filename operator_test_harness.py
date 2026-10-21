"""Deterministic miniature Operator journey. No API, LLM, MT5 or live market data."""
import json,tempfile
from pathlib import Path
from operator_handoff import *
def run():
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);a=r/"c.json";a.write_text(json.dumps({"state":"C_PASS","fixture":True}))
  ctest=envelope("C","FIX-001","v0",TEST,[("c_summary",a)],"C_TEST_FIXTURE")
  d_prod=validate(ctest,"C","FIX-001","v0")
  d_sandbox=validate(ctest,"C","FIX-001","v0",allow_test=True)
  b=r/"d.json";b.write_text(json.dumps({"state":"D_SANDBOX_PASS"}))
  dtest=envelope("D","FIX-001","v0",TEST,[("d_summary",b)],"D_SANDBOX_PASS")
  e_prod=validate(dtest,"D","FIX-001","v0")
  result={"state":"OPERATOR_TEST_HARNESS_PASS" if (not d_prod["pass"] and d_sandbox["pass"] and not e_prod["pass"]) else "OPERATOR_TEST_HARNESS_FAIL",
          "c_test_fixture_blocked_from_d_production":not d_prod["pass"],
          "c_test_fixture_allowed_in_d_sandbox":d_sandbox["pass"],
          "d_test_fixture_blocked_from_e_production":not e_prod["pass"]}
  return result
if __name__=="__main__":print(json.dumps(run(),indent=2))
