"""Fail-closed C stage gate predicates. No external workflow processing."""
def semantic_pass(obj):
    return (
        isinstance(obj,dict)
        and obj.get("state")=="SEMANTIC_GATE_PASS"
        and type(obj.get("failure_count")) is int
        and obj["failure_count"]==0
        and isinstance(obj.get("module_sha256"),str)
        and len(obj["module_sha256"])==64
    )

def stage1_completed(obj):
    return isinstance(obj,dict) and obj.get("state")=="STAGE1_COMPLETE"

def semantic_repair_authorized(semantic,release):
    return (
        isinstance(semantic,dict) and isinstance(release,dict)
        and semantic.get("state")=="SEMANTIC_GATE_HOLD"
        and type(semantic.get("failure_count")) is int
        and semantic["failure_count"]>0
        and isinstance(release.get("module_sha256"),str)
        and len(release["module_sha256"])==64
        and semantic.get("module_sha256")==release["module_sha256"]
    )
