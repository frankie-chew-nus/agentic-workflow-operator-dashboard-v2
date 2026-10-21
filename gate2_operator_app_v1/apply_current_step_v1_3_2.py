from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_current_step_v1_3_2.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

helper = '''
def embed_current_action_in_journey(page):
    if 'ACTION REQUIRED — HUMAN B→C REVIEW' not in page:
        return page
    start=page.find('<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b>')
    if start < 0:
        return page
    end=page.find('<div class=card><h2>Candidate pipeline</h2>',start)
    if end < 0:
        return page
    action=page[start:end]
    page=page[:start]+page[end:]
    action=action.replace('<div class="card action">','<div class="embedded-action">',1)
    marker='</section><div class="arrow">↓</div><section class="journey-card future">'
    pos=page.find(marker)
    if pos < 0:
        return page
    return page[:pos]+action+'</div></section><div class="arrow">↓</div><section class="journey-card future">'+page[pos+len(marker):]
'''

if "def embed_current_action_in_journey(" not in s:
    marker="def render():"
    if marker not in s: raise SystemExit("HOLD: render marker not found")
    s=s.replace(marker,helper+"\n"+marker,1)

old='return "<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>"'
new='return embed_current_action_in_journey("<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>")'
if "return embed_current_action_in_journey(" not in s:
    if old not in s: raise SystemExit("HOLD: final render expression not found")
    s=s.replace(old,new,1)

css_old="pre{white-space:pre-wrap;background:#f8fafc;padding:12px}"
css_new="pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto;border:1px solid #d1d5db;border-radius:8px}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}details summary{cursor:pointer;font-weight:700;color:#1d4ed8}.embedded-action{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.embedded-action h2{margin-top:8px}"
if ".embedded-action{" not in s:
    if css_old not in s: raise SystemExit("HOLD: CSS marker not found")
    s=s.replace(css_old,css_new,1)

tmp=Path("gate2.v132tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
Path("gate2.v13tmp.py").unlink(missing_ok=True)
Path("gate2.v131tmp.py").unlink(missing_ok=True)
print("OPERATOR_CURRENT_STEP_V1_3_2_APPLIED")
