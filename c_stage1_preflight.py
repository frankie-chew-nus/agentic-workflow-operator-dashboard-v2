"""Pre-run checks for existing C Stage1: no guessed plan sizes or PASS."""
import json
from pathlib import Path
def preflight(config,plan,semantic,runner=None):
    cfg=json.loads(Path(config).read_text(encoding="utf-8"))
    pl=json.loads(Path(plan).read_text(encoding="utf-8"))
    sem=json.loads(Path(semantic).read_text(encoding="utf-8"))
    count=len(pl.get("variants",[]))
    checks={"semantic_gate_pass":sem.get("state")=="SEMANTIC_GATE_PASS" and sem.get("failure_count")==0,
            "variant_count_is_50":count==50}
    if runner is not None:
        source=Path(runner).read_text(encoding="utf-8")
        checks["runner_semantic_contract"]=('sem.get("state")=="SEMANTIC_GATE_PASS"' in source and 'sem.get("module_sha256")==rec["module_sha256"]' in source)
    return {"state":"C_STAGE1_PREFLIGHT_READY" if all(checks.values()) else "C_STAGE1_PREFLIGHT_HOLD",
            "checks":checks,"variant_count":count,"expected_variant_count":50,
            "safe_to_run":all(checks.values())}
