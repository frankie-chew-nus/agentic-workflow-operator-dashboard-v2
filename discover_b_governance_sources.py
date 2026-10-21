"""Read-only discovery of trusted inputs needed before B policy integration.

Does not run B, change DB, inspect .env, or grant authority.
Outputs sanitized schema/table names and presence only, not row data.
"""
import json,sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OP=ROOT/"gate2_operator_app_v1"
DBS=[OP/"evidence"/"operator.db",OP/"evidence"/"state.db"]
CROOT=ROOT/"gate2_c_controller"
def inspect_db(p):
 result={"exists":p.is_file(),"tables":[],"candidate_release_count_authoritative":False}
 if not p.is_file():return result
 try:
  c=sqlite3.connect(f"file:{p.as_posix()}?mode=ro",uri=True)
  result["tables"]=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
  result["decision_columns"]=[r[1] for r in c.execute("PRAGMA table_info(decisions)")] if "decisions" in result["tables"] else []
  c.close()
 except sqlite3.Error as e:result["error_type"]=type(e).__name__
 return result
def main():
 report={"mode":"READ_ONLY_B_GOVERNANCE_SOURCE_DISCOVERY",
 "adapter_present":(OP/"b_resume.py").is_file(),
 "adapter_flow_present":(OP/"b_resume_model_flow_v1_1.py").is_file(),
 "databases":[{"location":str(p.relative_to(ROOT)),**inspect_db(p)} for p in DBS],
 "resource_inventory":"NOT_IDENTIFIED","dependency_allowlist":"NOT_IDENTIFIED",
 "commission_release_count":"NOT_VERIFIED","human_rule_change_authority":"NOT_VERIFIED",
 "production_authority":False,"writes_performed":False}
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
