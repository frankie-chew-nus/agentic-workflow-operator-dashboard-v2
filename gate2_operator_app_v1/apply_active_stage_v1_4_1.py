from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_active_stage_v1_4_1.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

# Remove any previous embed helper, then install the generic version.
st=s.find("def embed_current_action_in_journey(page):")
if st >= 0:
    en=s.find("\ndef render():",st)
    if en < 0: raise SystemExit("HOLD: old helper end not found")
    s=s[:st]+s[en+1:]

helper = '''
def embed_current_action_in_journey(page):
    candidates=[
      '<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b>',
      '<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b>',
      '<div class=card><b>ACTION REQUIRED</b><h2>Resume B</h2>'
    ]
    starts=[page.find(x) for x in candidates]
    starts=[x for x in starts if x >= 0]
    if not starts: return page
    start=min(starts)
    end=page.find('<div class=card><h2>Candidate pipeline</h2>',start)
    if end < 0: return page
    action=page[start:end]
    page=page[:start]+page[end:]
    action=action.replace('<div class="card action">','<div class="embedded-action">',1)
    action=action.replace('<div class="card hold">','<div class="embedded-action hold-inline">',1)
    action=action.replace('<div class=card>','<div class="embedded-action">',1)
    if 'View corrected specification' not in action and 'View last corrected specification' not in action:
        rel=review_data()
        if rel and rel.get('candidate'):
            cand=rel['candidate']
            evidence='<details><summary>View last corrected specification</summary><pre>'+html.escape(json.dumps(cand,indent=2))+'</pre></details>'
            close=action.rfind('</div>')
            if close >= 0: action=action[:close]+evidence+action[close:]
    marker='</section><div class="arrow">↓</div><section class="journey-card future">'
    pos=page.find(marker)
    if pos < 0: return page
    return page[:pos]+action+'</div></section><div class="arrow">↓</div><section class="journey-card future">'+page[pos+len(marker):]
'''

marker="def render():"
if marker not in s: raise SystemExit("HOLD: render marker not found")
s=s.replace(marker,helper+"\n"+marker,1)

plain='return "<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>"'
wrapped='return embed_current_action_in_journey("<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>")'
if wrapped not in s:
    if plain not in s: raise SystemExit("HOLD: final render expression not found")
    s=s.replace(plain,wrapped,1)

# Ensure presentation CSS exists.
if ".embedded-action{" not in s:
    anchor="pre{white-space:pre-wrap;background:#f8fafc;padding:12px}"
    repl="pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto;border:1px solid #d1d5db;border-radius:8px}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}details summary{cursor:pointer;font-weight:700;color:#1d4ed8}.embedded-action{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.embedded-action h2{margin-top:8px}.hold-inline{border-left:5px solid #d97706;padding-left:14px}"
    if anchor not in s: raise SystemExit("HOLD: CSS anchor not found")
    s=s.replace(anchor,repl,1)

tmp=Path("gate2.v141tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
Path("gate2.v14tmp.py").unlink(missing_ok=True)
print("OPERATOR_ACTIVE_STAGE_V1_4_1_APPLIED")
