"""Read-only Stage 1 execution diagnostics from existing controller log and outputs."""
import json,re
from pathlib import Path

def diagnose(runroot,logpath=None):
    root=Path(runroot);summary_file=root/"c_run_summary.json"
    summary=json.loads(summary_file.read_text(encoding="utf-8")) if summary_file.exists() else {}
    output=Path(summary.get("output_dir") or root/"stage1_output")
    log=Path(logpath) if logpath else root.parent.parent.parent/"logs"/("C-RUN-"+root.parent.name+"-"+root.name.replace(".","_")+".log")
    raw=log.read_text(encoding="utf-8",errors="replace") if log.exists() else ""
    marker="stage1_runner_v3.py"
    index=raw.rfind(marker)
    stage_log=raw[index:] if index>=0 else ""
    hold_tokens=sorted(set(re.findall(r'(?i)(?:HOLD_FOR_HUMAN|SEMANTIC_GATE_HOLD|STAGE1_[A-Z_]*HOLD|HOLD:\s*[^\n]{0,180})',stage_log)))
    result={
        "state":"C_STAGE1_EXECUTION_DIAGNOSIS",
        "output_directory":str(output),
        "output_directory_exists":output.is_dir(),
        "log_path":str(log),
        "log_exists":log.exists(),
        "stage1_command_seen":index>=0,
        "stage1_log_tail":stage_log[-12000:],
        "reported_holds":hold_tokens,
        "finding":"Stage 1 command was recorded but authoritative output directory is missing." if not output.is_dir() else "Stage 1 output directory exists; verify authoritative summary.",
        "safe_to_advance_to_d":False
    }
    out=root/"stage1_execution_diagnosis.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--run-root",required=True);p.add_argument("--log");a=p.parse_args()
    print(json.dumps(diagnose(a.run_root,a.log),indent=2))
