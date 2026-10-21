"""Stage 1 authoritative evidence resolution. No inferred PASS or D handoff."""
import json
from pathlib import Path

def resolve_stage1(output_dir):
    root=Path(output_dir)
    if not root.is_dir():
        return {"state":"C_STAGE1_EVIDENCE_HOLD","reason":"OUTPUT_DIRECTORY_MISSING","files":[]}
    files=[p for p in sorted(root.rglob("*")) if p.is_file()]
    summaries=[]
    for p in files:
        if p.suffix.lower()!=".json":continue
        try: obj=json.loads(p.read_text(encoding="utf-8"))
        except (OSError,ValueError):continue
        if not isinstance(obj,dict) or obj.get("state")!="STAGE1_COMPLETE":continue
        fields=("variant_count","pass_count","fail_count","human_hold_count")
        if not all(type(obj.get(k)) is int and obj[k]>=0 for k in fields):continue
        if obj["pass_count"]+obj["fail_count"]+obj["human_hold_count"]>obj["variant_count"]:continue
        summaries.append((p,obj))
    if len(summaries)!=1:
        return {"state":"C_STAGE1_EVIDENCE_HOLD","reason":"NO_AUTHORITATIVE_SUMMARY" if not summaries else "AMBIGUOUS_AUTHORITATIVE_SUMMARIES",
                "files":[str(p) for p in files],"summary_count":len(summaries)}
    path,obj=summaries[0]
    return {"state":"C_STAGE1_REVIEW_REQUIRED","summary_path":str(path.resolve()),
            "metrics":{k:obj[k] for k in ("variant_count","pass_count","fail_count","human_hold_count")},
            "files":[str(p) for p in files],"advance_to_d":False}
