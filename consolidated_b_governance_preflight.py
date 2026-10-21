"""Consolidated B governance preflight, experimental only.

All authoritative inputs are supplied by a separate trusted caller. This function
never reads candidate-supplied release counts or approval claims as authority.
No production release is possible from this module.
"""
from b_boundary_policy_v1 import validate_boundary
from b_commission_release_ledger_v1 import validate_ledger
from b_policy_change_gate_v1 import authorize_change

def evaluate(candidate,context):
 if not isinstance(candidate,dict) or not isinstance(context,dict):
  return {"state":"GOVERNANCE_HOLD","failures":["INVALID_INPUT"],"production_authority":False}
 if context.get("fixture_only") is not True:
  return {"state":"GOVERNANCE_HOLD","failures":["TRUSTED_CONTEXT_UNVERIFIED"],"production_authority":False}
 required=("available_resources","approved_dependencies","release_ledger","commission_id",
           "verified_decision_ids","prior_policy","trusted_prior_policy_digest")
 if any(k not in context for k in required):
  return {"state":"GOVERNANCE_HOLD","failures":["TRUSTED_INPUTS_MISSING"],"production_authority":False}
 ledger=context["release_ledger"]
 releases=ledger.get("releases") if isinstance(ledger,dict) else None
 failures=validate_ledger(ledger,context["commission_id"],candidate.get("candidate_id"),
                         verified_decision_ids=context["verified_decision_ids"])
 failures+=validate_boundary(candidate,available_resources=context["available_resources"],
     approved_dependencies=context["approved_dependencies"],
     released_count=len(releases) if isinstance(releases,list) else None,
     human_rule_change_approved=False)
 if "governance_rule_change" in candidate:
  change=context.get("policy_change")
  if not isinstance(change,dict):
   failures.append("POLICY_CHANGE_RECORD_MISSING")
  else:
   failures+=authorize_change(context["prior_policy"],change.get("proposed_policy"),
       change.get("decision"),trusted_decision_ids=context.get("trusted_policy_decision_ids"),
       trusted_previous_digest=context["trusted_prior_policy_digest"])
 # An approved policy change cannot override the immutable three-candidate ceiling.
 return {"state":"GOVERNANCE_HOLD" if failures else "PREFLIGHT_PASS_TEST_ONLY",
         "failures":sorted(set(failures)),"production_authority":False}
