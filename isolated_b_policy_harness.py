"""Isolated policy integration harness. Never imports/runs active B adapter or opens production DB.

Uses synthetic inputs and trusted fixture context supplied separately from candidate payload.
Not a production integration and grants no release authority.
"""
from b_boundary_policy_v1 import validate_boundary

def evaluate(candidate, trusted_context):
    if not isinstance(trusted_context,dict):
        return {"state":"GOVERNANCE_HOLD","failures":["TRUSTED_CONTEXT_MISSING"],"production_authority":False}
    failures=validate_boundary(
        candidate,
        available_resources=trusted_context.get("available_resources"),
        approved_dependencies=trusted_context.get("approved_dependencies"),
        released_count=trusted_context.get("released_count"),
        human_rule_change_approved=trusted_context.get("human_rule_change_approved",False),
    )
    return {"state":"GOVERNANCE_HOLD" if failures else "ELIGIBLE_FOR_EXISTING_B_CHECKS",
            "failures":failures,"production_authority":False}
