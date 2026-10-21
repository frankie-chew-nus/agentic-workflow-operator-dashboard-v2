"""Candidate B->C release guard for future integration. NOT active or approved.

A trusted host must supply the decision on whether all four controls have been
independently verified. Candidate, request form and dashboard state are untrusted.
This module never grants release authority on its own.
"""
CONTROLS=("T04","T05","T09","T10")

def release_preflight(*, candidate_id, research_id, verified_context=None):
    failures=[]
    if not candidate_id or not research_id:
        failures.append("IDENTITY_MISSING")
    if not isinstance(verified_context,dict):
        return {"state":"GOVERNANCE_HOLD","failures":["TRUSTED_CONTEXT_MISSING"],"release_authorized":False}
    if verified_context.get("authority_source")!="INDEPENDENT_OPERATOR_REGISTER":
        failures.append("AUTHORITY_SOURCE_UNVERIFIED")
    if verified_context.get("candidate_id")!=candidate_id or verified_context.get("research_id")!=research_id:
        failures.append("CONTEXT_IDENTITY_MISMATCH")
    if verified_context.get("production_authority") is not False:
        failures.append("PRODUCTION_AUTHORITY_FORBIDDEN")
    for control in CONTROLS:
        record=verified_context.get("controls",{}).get(control) if isinstance(verified_context.get("controls"),dict) else None
        if not isinstance(record,dict) or record.get("status")!="VERIFIED" or not record.get("evidence_sha256"):
            failures.append(control+"_NOT_VERIFIED")
    # Deliberately no release-allowed return value: host integration and independent
    # authentication are not implemented. Passing structural checks is insufficient.
    return {"state":"GOVERNANCE_HOLD","failures":sorted(set(failures+["LIVE_AUTHORITY_BINDING_NOT_IMPLEMENTED"])),
            "release_authorized":False}
