from pathlib import Path
import py_compile
p=Path("gate2.py");s=p.read_text(encoding="utf-8");backup=Path("gate2.pre_v1_1.py")
if backup.exists():raise SystemExit("HOLD: backup already exists")
# UI accepts either historical field name.
old='cand.get("operator_assumptions",{}).get("volatility_expansion_definition","")'
new='(cand.get("operator_assumptions",{}).get("volatility_expansion_definition") or cand.get("operator_assumptions",{}).get("volatility_expansion_condition",""))'
if old not in s:raise SystemExit("HOLD: expected UI mapping not found")
s=s.replace(old,new)
tmp=Path("gate2.v11tmp.py");tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
backup.write_text(p.read_text(encoding="utf-8"),encoding="utf-8");p.write_text(s,encoding="utf-8");tmp.unlink()
print("OPERATOR_UI_V1_1_PATCHED")
