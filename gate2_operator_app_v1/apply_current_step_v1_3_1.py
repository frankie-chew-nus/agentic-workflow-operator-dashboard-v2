from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists():
    raise SystemExit("HOLD: gate2.py not found")

# The failed v1.3 patch compiled only a temp file and did not overwrite gate2.py.
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_current_step_v1_3_1.py")
if bak.exists():
    raise SystemExit("HOLD: backup already exists")

# Inject a helper that moves the already-rendered standalone B review card
# into the active B journey card. This changes presentation only.
helper = r