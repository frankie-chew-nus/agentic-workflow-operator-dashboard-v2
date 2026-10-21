"""Read-only Stage 1 evidence inventory; never infer PASS from process exit."""
import json
from pathlib import Path

def inspect(summary):
    output=Path(summary.get("output_dir") or "")
    files=[]
    if output.is_dir():
        for p in sorted(output.rglob("*.json"))[:200]:
            try:
                obj=json.loads(p.read_text(encoding="utf-8"))
            except (OSError,ValueError):
                continue
            if not isinstance(obj,dict):continue
            files.append({"path":str(p),"state":obj.get("state"),"pass_count":obj.get("pass_count"),
                          "fail_count":obj.get("fail_count"),"human_hold_count":obj.get("human_hold_count")})
    summaries=[x for x in files if x["state"]=="STAGE1_COMPLETE"]
    return {"state":"C_STAGE1_EVIDENCE_REVIEW","candidate_id":summary.get("candidate_id"),
            "version":summary.get("version"),"files":files,
            "authoritative_summaries":summaries,
            "review_status":"SUMMARY_FOUND_REVIEW_REQUIRED" if summaries else "MISSING_STAGE1_SUMMARY_HOLD",
            "auto_pass":False,"advance_to_d":False}
