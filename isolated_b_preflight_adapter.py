"""Isolated B preflight adapter. No production database or release authority.

Trusted context is supplied by the caller, never extracted from candidate fields.
Policy draft must remain unapproved; this module is for synthetic tests only.
"""
from b_boundary_policy_v1 import validate_boundary

def preflight(candidate, context):
    if not isinstance(context,dict) or context.get("fixture_only") is not True:
        return {"state":"GOVERNANCE_HOLD","failures":["UNVERIFIED_TRUSTED_CONTEXT"],"production_authority":False}
    if context.get("policy_status")!="SYNTHETIC_TEST_ONLY":
        return {"state":"GOVERNANCE_HOLD","failures":["POLICY_NOT_TEST_FIXTURE"],"production_authority":False}
    failures=validate_boundary(candidate,
        available_resources=context.get("available_resources"),
        approved_dependencies=context.get("approved_dependencies"),
        released_count=context.get("released_count"),
        human_rule_change_approved=False)
    return {"state":"GOVERNANCE_HOLD" if failures else "PREFLIGHT_PASS_TEST_ONLY",
            "failures":failures,"production_authority":False}
