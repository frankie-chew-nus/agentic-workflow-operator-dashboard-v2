from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_log_expand_v1_4_2.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

# Add safe log rendering helper before render().
helper = '''
def expandable_log_html(log_path):
    try:
        p=Path(log_path)
        if not p.exists():
            return '<details><summary>View failure log</summary><pre>Log file not found: '+html.escape(str(p))+'</pre></details>'
        text=p.read_text(encoding='utf-8',errors='replace')
        return '<details><summary>View failure log</summary><pre>'+html.escape(text)+'</pre></details>'
    except Exception as e:
        return '<details><summary>View failure log</summary><pre>Unable to read log: '+html.escape(str(e))+'</pre></details>'
'''

if "def expandable_log_html(" not in s:
    marker="def render():"
    if marker not in s: raise SystemExit("HOLD: render marker not found")
    s=s.replace(marker,helper+"\n"+marker,1)

# Enhance SYSTEM_HOLD card only. Put expandable log before textarea/form.
old='''b+=\'<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b><h2>CAND-B-002</h2><p>\'+html.escape(x["detail"])+\'</p><form method=post action=/decide><textarea name=rationale required minlength=12></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RETRY_B>Retry same B work</button></form></div>\''''
new='''b+=\'<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b><h2>CAND-B-002</h2><p>\'+html.escape(x["detail"])+\'</p>\'+expandable_log_html(x["detail"].split("View ",1)[1] if "View " in x["detail"] else "")+\'<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="Human rationale"></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RETRY_B>Retry same B work</button></form></div>\''''
if "expandable_log_html(x[" not in s:
    if old not in s: raise SystemExit("HOLD: SYSTEM_HOLD renderer not found")
    s=s.replace(old,new,1)

tmp=Path("gate2.v142tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
print("OPERATOR_LOG_EXPAND_V1_4_2_APPLIED")
