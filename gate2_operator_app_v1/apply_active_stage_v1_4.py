from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_active_stage_v1_4.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

# Replace the narrow v1.3 embed helper with a generic current-action embedder.
start=s.find("def embed_current_action_in_journey(page):")
if start >= 0:
    end=s.find("\ndef render():",start)
    if end < 0: raise SystemExit("HOLD: could not locate end of old embed helper")
    s=s[:start]+s[end+1:]

helper = r