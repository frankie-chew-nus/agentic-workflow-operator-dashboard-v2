"""Experimental release authority binding; never grants live release.

Separates authenticated, externally verified authority from mere structural claims.
A trusted host must supply a verifier callback; without it the result is HOLD.
This is test-only and must not be installed in active dashboard.
"""
from b_release_guard_candidate import release_preflight

def evaluate_release(candidate_id,research_id,context,*,verifier=None,disposable=False):
    baseline=release_preflight(candidate_id=candidate_id,research_id=research_id,verified_context=context)
    if not disposable:
        return {"state":"GOVERNANCE_HOLD","release_authorized":False,"failures":["ACTIVE_INTEGRATION_NOT_APPROVED"]}
    if not callable(verifier):
        return {"state":"GOVERNANCE_HOLD","release_authorized":False,"failures":["INDEPENDENT_VERIFIER_MISSING"]}
    if not isinstance(context,dict):
        return baseline
    # Structural checks are useful, but LIVE_AUTHORITY_BINDING_NOT_IMPLEMENTED
    # must never be interpreted as a positive authorization.
    structural=[x for x in baseline["failures"] if x!="LIVE_AUTHORITY_BINDING_NOT_IMPLEMENTED"]
    if structural:
        return {"state":"GOVERNANCE_HOLD","release_authorized":False,"failures":structural}
    try:
        verified=verifier(candidate_id,research_id,context)
    except Exception:
        verified=False
    if verified is not True:
        return {"state":"GOVERNANCE_HOLD","release_authorized":False,"failures":["INDEPENDENT_VERIFICATION_FAILED"]}
    return {"state":"DISPOSABLE_RELEASE_ELIGIBLE","release_authorized":True,"failures":[],
            "production_authority":False}
