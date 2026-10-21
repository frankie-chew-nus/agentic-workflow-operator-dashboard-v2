"""Read-only B policy input review; proposed values are NOT approvals.

Reads the frozen B register locally. Never opens DB, .env, or modifies artifacts.
Displays only declared input/dependency identifiers, not strategy logic.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REG=ROOT/"gate2_c_controller"/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"
def main():
 if not REG.is_file():raise SystemExit("Frozen B register not found")
 d=json.loads(REG.read_text(encoding="utf-8"))
 rows=[]
 for c in d.get("candidates",[]):
  rows.append({
   "candidate_id":c.get("candidate_id"),
   "required_inputs":c.get("required_inputs",[]),
   "declared_prohibited_dependencies":c.get("prohibited_dependencies",[]),
   "explicit_dependencies":c.get("dependencies",None),
   "required_resources":c.get("required_resources",None)
  })
 print(json.dumps({"mode":"READ_ONLY_B_POLICY_REVIEW",
  "source":"gate2_c_controller/inputs/candidate_strategy_register_v2_1_1_frozen.json",
  "candidates":rows,
  "approved_resource_inventory":"NOT_ESTABLISHED",
  "approved_dependency_allowlist":"NOT_ESTABLISHED",
  "note":"Declared inputs and prohibitions are NOT verified availability or dependency approval.",
  "writes_performed":False,"production_authority":False},indent=2))
if __name__=="__main__":main()
