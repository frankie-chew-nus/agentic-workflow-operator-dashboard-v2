"""Guarded compatibility repair for authoritative C Stage 1 semantic state."""
from pathlib import Path
import argparse,shutil,py_compile
OLD='sem.get("state")=="SEMANTIC_V2_PASS"'
NEW='sem.get("state")=="SEMANTIC_GATE_PASS"'
def apply(path):
    path=Path(path);text=path.read_text(encoding="utf-8")
    if OLD not in text:
        if NEW in text:return "ALREADY_APPLIED"
        raise RuntimeError("HOLD: unknown Stage1 semantic contract")
    if text.count(OLD)!=1 or 'sem.get("module_sha256")==rec["module_sha256"]' not in text:
        raise RuntimeError("HOLD: unexpected Stage1 gate")
    fixed=text.replace(OLD,NEW);compile(fixed,str(path),"exec")
    backup=path.with_suffix(".pre_semantic_contract_fix.py")
    if backup.exists():raise RuntimeError("HOLD: backup exists")
    shutil.copy2(path,backup)
    try:
        path.write_text(fixed,encoding="utf-8",newline="")
        py_compile.compile(str(path),doraise=True)
    except Exception:
        shutil.copy2(backup,path);raise
    return "STAGE1_SEMANTIC_CONTRACT_FIXED"
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--c-root",required=True);a=p.parse_args()
    print(apply(Path(a.c_root)/"stage1_runner_v3.py"))
