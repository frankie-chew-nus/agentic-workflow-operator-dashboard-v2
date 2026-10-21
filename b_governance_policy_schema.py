"""Schema checks for DRAFT B policy; no authority can be inferred from placeholders."""
import json
from pathlib import Path

REQUIRED=("schema_version","policy_id","status","research_commission_id",
 "approved_resources","approved_dependencies","max_released_candidates",
 "release_ledger","rule_change_approval","operator_approval","production_authority")
def validate_policy(policy):
 errors=[]
 if not isinstance(policy,dict):return ["POLICY_NOT_OBJECT"]
 for k in REQUIRED:
  if k not in policy:errors.append("MISSING_FIELD:"+k)
 if errors:return errors
 if policy["schema_version"]!="B_GOVERNANCE_POLICY_V1":errors.append("SCHEMA_VERSION_INVALID")
 if policy["max_released_candidates"]!=3:errors.append("COMMISSION_LIMIT_INVALID")
 if policy["production_authority"] is not False:errors.append("PRODUCTION_AUTHORITY_FORBIDDEN")
 if policy["status"]!="APPROVED":errors.append("POLICY_NOT_APPROVED")
 if not isinstance(policy["operator_approval"],dict) or not all(policy["operator_approval"].get(k) for k in ("decision_id","approved_at","policy_sha256")):
  errors.append("HUMAN_APPROVAL_MISSING")
 if not isinstance(policy["approved_resources"],list):errors.append("RESOURCE_INVENTORY_MISSING")
 if not isinstance(policy["approved_dependencies"],list):errors.append("DEPENDENCY_ALLOWLIST_MISSING")
 if not policy["research_commission_id"]:errors.append("RESEARCH_COMMISSION_MISSING")
 if not isinstance(policy["release_ledger"],dict) or not policy["release_ledger"].get("verified_source"):
  errors.append("RELEASE_LEDGER_UNVERIFIED")
 if not isinstance(policy["rule_change_approval"],dict):errors.append("RULE_CHANGE_AUTHORITY_MISSING")
 return errors
def load_draft():
 return json.loads((Path(__file__).resolve().parent/"b_governance_policy_v1.draft.json").read_text(encoding="utf-8"))
