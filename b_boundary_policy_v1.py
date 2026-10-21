"""Fail-closed B boundary policy checks, separate from strategy logic.

This module is a proposed guard for integration with the external B resume adapter.
It does not grant RELEASE_TO_C authority.
"""
from pathlib import Path

SENSITIVE={"required_resources","dependencies","research_commission_release_count","governance_rule_change"}

def validate_boundary(candidate, *, available_resources, approved_dependencies,
                      released_count, human_rule_change_approved=False):
    failures=[]
    # Fail closed if a candidate attempts to supply governance facts itself.
    if "research_commission_release_count" in candidate:
        failures.append("UNTRUSTED_COMMISSION_COUNT")
    if "governance_rule_change" in candidate and not human_rule_change_approved:
        failures.append("UNAUTHORIZED_RULE_CHANGE")
    # Resource/dependency data must come from an authorized inventory.
    if available_resources is None:
        failures.append("RESOURCE_INVENTORY_UNAVAILABLE")
    else:
        for r in candidate.get("required_resources",[]):
            if r not in available_resources:failures.append("RESOURCE_UNAVAILABLE:"+str(r))
    if approved_dependencies is None:
        failures.append("DEPENDENCY_ALLOWLIST_UNAVAILABLE")
    else:
        for d in candidate.get("dependencies",[]):
            if d not in approved_dependencies:failures.append("DEPENDENCY_NOT_APPROVED:"+str(d))
    if released_count is None:
        failures.append("RELEASE_COUNT_UNVERIFIED")
    elif released_count>=3:
        failures.append("COMMISSION_LIMIT_REACHED")
    return sorted(set(failures))
