"""Experimental commission release ledger validation. No live authority.

Records are append-only in the eventual design; this module only validates snapshots.
Candidate-provided counts, unsigned decisions, and unverified histories cannot authorize release.
"""
def validate_ledger(ledger, commission_id, candidate_id, *, verified_decision_ids=None):
    failures=[]
    if not isinstance(ledger,dict) or ledger.get("schema")!="COMMISSION_LEDGER_V1":
        return ["LEDGER_UNVERIFIED"]
    if ledger.get("commission_id")!=commission_id or not commission_id:
        failures.append("COMMISSION_ID_MISMATCH")
    if ledger.get("status")!="VERIFIED_BY_OPERATOR":
        failures.append("LEDGER_NOT_VERIFIED")
    entries=ledger.get("releases")
    if not isinstance(entries,list):
        return sorted(set(failures+["RELEASE_HISTORY_MISSING"]))
    seen=set()
    for entry in entries:
        if not isinstance(entry,dict):
            failures.append("MALFORMED_RELEASE");continue
        cid=entry.get("candidate_id")
        did=entry.get("human_decision_id")
        if not cid or not did or not entry.get("release_artifact_sha256"):
            failures.append("INCOMPLETE_RELEASE_PROVENANCE")
        if cid in seen:failures.append("DUPLICATE_CANDIDATE_RELEASE")
        seen.add(cid)
        if verified_decision_ids is None or did not in verified_decision_ids:
            failures.append("HUMAN_DECISION_NOT_VERIFIED")
    if candidate_id in seen:failures.append("CANDIDATE_ALREADY_RELEASED")
    if len(seen)>=3:failures.append("COMMISSION_LIMIT_REACHED")
    return sorted(set(failures))
