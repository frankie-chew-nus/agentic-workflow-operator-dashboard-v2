"""Guarded repair of the authoritative C Stage1 runner to the current module contract.

Changes only interface plumbing:
- prepare(history, params) -> prepare(history)
- signal_at(i, prepared, params) -> signal(history[:i+1], prepared_prefix, params)
The runner's risk/execution model is otherwise left untouched. If its parameter
requirements are incompatible with the frozen variant plan, preflight must HOLD.
"""
from pathlib import Path
import argparse,py_compile,shutil

OLD_PREP='prepared=m.prepare(bars,par)'
NEW_PREP='prepared=m.prepare(bars)'
OLD_SIG='sig=m.signal_at(i,prepared,par)'
NEW_SIG='prefix=bars[:i+1];prepared_i=m.prepare(prefix);sig=m.signal(prefix,prepared_i,par)'

def apply(path):
    path=Path(path);src=path.read_text(encoding="utf-8")
    if OLD_PREP not in src and OLD_SIG not in src:
        if NEW_PREP in src and NEW_SIG in src:return "ALREADY_APPLIED"
        raise RuntimeError("HOLD: unknown Stage1 strategy interface")
    if src.count(OLD_PREP)!=1 or src.count(OLD_SIG)!=1:
        raise RuntimeError("HOLD: unexpected Stage1 interface; no changes made")
    fixed=src.replace(OLD_PREP,NEW_PREP).replace(OLD_SIG,NEW_SIG)
    compile(fixed,str(path),"exec")
    backup=path.with_suffix(".pre_interface_contract_fix.py")
    if backup.exists():raise RuntimeError("HOLD: interface backup already exists")
    shutil.copy2(path,backup)
    try:
        path.write_text(fixed,encoding="utf-8",newline="")
        py_compile.compile(str(path),doraise=True)
    except Exception:
        shutil.copy2(backup,path);raise
    return "STAGE1_STRATEGY_INTERFACE_FIXED"

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--c-root",required=True);a=p.parse_args()
    print(apply(Path(a.c_root)/"stage1_runner_v3.py"))
