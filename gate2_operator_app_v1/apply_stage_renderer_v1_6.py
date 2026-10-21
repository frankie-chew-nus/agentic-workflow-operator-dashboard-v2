from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_stage_renderer_v1_6.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

# 1) Make aggregate NO_REGRESSION fail whenever protected cumulative rules fail.
old="""failed_ids=set()
    for f in fails:
        key=f.split(':',1)[0]; failed_ids.add(mapping.get(key,key))"""
new="""failed_ids=set()
    for f in fails:
        key=f.split(':',1)[0]; failed_ids.add(mapping.get(key,key))
    protected={'STRICT_NR_N','VOL_RULE','VOL_ENTRY','ATR_DEFAULT','HYPOTHESIS','EVIDENCE','PARAMETERS','DEPENDENCIES'}
    if failed_ids & protected: failed_ids.add('NO_REGRESSION')"""
if old in s: s=s.replace(old,new,1)

# 2) Add observed/expected diagnostics to governance table.
oldhead="<table class=\"rules\"><tr><th></th><th>Rule</th><th>Requirement</th></tr>"
newhead="<table class=\"rules\"><tr><th></th><th>Rule</th><th>Requirement</th><th>Observed / expected</th></tr>"
if oldhead in s: s=s.replace(oldhead,newhead,1)
# Replace row construction with diagnostic column when exact fragment exists.
oldrow="rows[-1]+='><td>'+('✗' if bad else '✓')+'</td><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['label'])+'</td></tr>'"
newrow="""diag=''
        if bad:
            if r['id']=='VERSION': diag='Expected '+str(hold.get('parent_version',''))+' next patch version; attempted '+str(hold.get('attempted_version',''))
            elif r['id']=='STRICT_NR_N': diag='Expected strict < semantics throughout; attempted revision did not preserve them.'
            elif r['id']=='VOL_RULE': diag='Expected deterministic breakout-range > preceding-N average rule; rule missing/regressed.'
            elif r['id']=='VOL_ENTRY': diag='Expected volatility confirmation in both long and short entries; missing/regressed.'
            elif r['id']=='NO_REGRESSION': diag='One or more previously accepted protected requirements regressed.'
            else: diag='Contract check failed.'
        rows[-1]+='><td>'+('✗' if bad else '✓')+'</td><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['label'])+'</td><td>'+html.escape(diag)+'</td></tr>'"""
if oldrow in s: s=s.replace(oldrow,newrow,1)

# 3) Replace embed helper with a generic stage-owned panel mover that handles RUNNING too.
st=s.find("def embed_current_action_in_journey(page):")
if st >= 0:
    en=s.find("\ndef render():",st)
    if en < 0: raise SystemExit("HOLD: embed helper end not found")
    s=s[:st]+s[en+1:]

helper = '''
def embed_current_action_in_journey(page):
    # Current-stage operational panels must live inside the active A-E stage.
    signatures=[
      '<div class=card><b>RUNNING</b>',
      '<div class=card><b>RUNNING — NO ACTION REQUIRED</b>',
      '<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b>',
      '<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b>',
      '<div class="card hold"><b>ACTION REQUIRED — GOVERNANCE HOLD</b>',
      '<div class=card><b>ACTION REQUIRED</b><h2>Resume B</h2>'
    ]
    found=[page.find(x) for x in signatures]
    found=[x for x in found if x>=0]
    if not found: return page
    start=min(found)
    end=page.find('<div class=card><h2>Candidate pipeline</h2>',start)
    if end<0: return page
    panel=page[start:end]
    page=page[:start]+page[end:]
    panel=panel.replace('<div class="card action">','<div class="embedded-action">',1)
    panel=panel.replace('<div class="card hold">','<div class="embedded-action hold-inline">',1)
    panel=panel.replace('<div class=card>','<div class="embedded-action">',1)
    marker='</section><div class="arrow">↓</div><section class="journey-card future">'
    pos=page.find(marker)
    if pos<0: return page
    return page[:pos]+panel+'</div></section><div class="arrow">↓</div><section class="journey-card future">'+page[pos+len(marker):]
'''
marker="def render():"
if marker not in s: raise SystemExit("HOLD: render marker not found")
s=s.replace(marker,helper+"\n"+marker,1)

# 4) Ensure final renderer invokes stage-owned embedding.
plain='return "<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>"'
wrapped='return embed_current_action_in_journey("<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>")'
if wrapped not in s:
    if plain not in s: raise SystemExit("HOLD: final render expression not found")
    s=s.replace(plain,wrapped,1)

# 5) Make B journey header state derive from actual job/state rather than always HUMAN ACTION REQUIRED.
oldstatus='''status="HUMAN ACTION REQUIRED" if ac and ac["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else "WORKFLOW ACTIVE"'''
newstatus='''status=("RUNNING — NO ACTION REQUIRED" if ac and ac["state"]=="B_RUNNING" else ("HUMAN ACTION REQUIRED" if ac and ac["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else "WORKFLOW ACTIVE"))'''
if oldstatus in s: s=s.replace(oldstatus,newstatus,1)

# 6) Friendly CSS for diagnostic column.
if ".rules td:last-child{" not in s:
    csspos=s.find('css="body{')
    if csspos<0: raise SystemExit("HOLD: css assignment not found")
    end=s.find('"\n return ',csspos)
    if end<0: raise SystemExit("HOLD: css end not found")
    extra=".rules td:last-child{max-width:420px;color:#4b5563}.rule-fail td:last-child{color:#991b1b}.embedded-action{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}"
    s=s[:end]+extra+s[end:]

tmp=Path("gate2.v16tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
print("OPERATOR_STAGE_RENDERER_V1_6_APPLIED")
