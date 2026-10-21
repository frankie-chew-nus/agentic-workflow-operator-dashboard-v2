from pathlib import Path
import py_compile

p=Path("gate2.py")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_full_journey_v1_2.py")
if bak.exists():
    raise SystemExit("HOLD: backup already exists")

helper = """
def journey_html(c,r,cs):
    active_stage=r["stage"]
    ac=next((x for x in cs if x["state"] in ("B_RUNNING","B_REVIEW","WAITING_FOR_B","READY_FOR_C","C_RUNNING","D_RUNNING","E_RUNNING","SYSTEM_HOLD","GOVERNANCE_HOLD")),None)
    defs={
      "A":("Research & Source Qualification","Grounded Researcher + Human Operator","Approved research evidence package / source register","Only Human-approved A evidence enters B.","Public evidence is qualified and frozen; B has no independent retrieval authority."),
      "B":("Evidence Synthesis & Strategy Formulation","Knowledge Archivist + Strategy Optimizer + Human Operator","Versioned Candidate Strategy Specifications","Human RELEASE / RETURN TO B / REJECT before C.","B owns the strategy concept and search envelope; returned candidates are reformulated and reassessed."),
      "C":("Local Integration & Stage 1 Backtesting","Existing local C CLI / Local Backtest Runner","Reproducible Stage 1 build, ledger, metrics, logs and hashes","Only C-PASS frozen candidate/version may proceed to D.","C operates within B authority; mandatory friction remains 9 pips."),
      "D":("Hidden OOS / Walk-Forward Validation","Local deterministic harness + MT5 + Human OOS boundary","Independent OOS ledger, metrics and integrity evidence","D PASS may proceed to E; D FAIL is withheld; integrity defects HOLD.","D uses unseen MT5 evidence and may not optimise against it."),
      "E":("Commissioning Audit & Decision","Human Operator + deterministic commissioning checks","Signed commissioning decision and frozen installation record","Terminal APPROVE / REJECT / CLOSE.","Human owns live-capital commissioning authority.")
    }
    order="ABCDE"
    idx=order.index(active_stage) if active_stage in order else 0
    cards=[]
    for i,k in enumerate(order):
        title,owner,output,handoff,detail=defs[k]
        if i<idx:
            state,status,cls="FROZEN","HANDED OVER TO "+order[i+1],"done"
        elif i==idx:
            state="ACTIVE"
            status="HUMAN ACTION REQUIRED" if ac and ac["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else "WORKFLOW ACTIVE"
            cls="active"
        else:
            state,status,cls="NOT STARTED","Awaiting "+order[i-1]+" handoff","future"
        extra=""
        if k=="B" and ac:
            extra="<p><b>Current candidate:</b> "+html.escape(ac["id"])+" · "+html.escape(ac["version"] or "")+" · "+html.escape(ac["state"])+"</p><p><b>Current detail:</b> "+html.escape(ac["detail"])+"</p>"
        cards.append('<section class="journey-card '+cls+'"><div class="journey-head"><span class="stage-letter">'+k+'</span><div><b>'+html.escape(title)+'</b><div class="state">'+state+' · '+status+'</div></div></div><p><b>Owner:</b> '+html.escape(owner)+'</p><p><b>Produces:</b> '+html.escape(output)+'</p><p><b>Handoff:</b> '+html.escape(handoff)+'</p><p><b>Operating context:</b> '+html.escape(detail)+'</p>'+extra+'</section>')
    return '<div class="card"><h2>Full research journey</h2><p class="muted">Persistent A→E context, evidence lineage and current operating position.</p><div class="journey">'+'<div class="arrow">↓</div>'.join(cards)+'</div></div>'
"""

if "def journey_html(" not in s:
    if "def render():" not in s: raise SystemExit("HOLD: render marker not found")
    s=s.replace("def render():",helper+"\ndef render():",1)

if "b+=journey_html(c,r,cs)" not in s:
    if "if job:" not in s: raise SystemExit("HOLD: job marker not found")
    s=s.replace("if job:","b+=journey_html(c,r,cs)\n if job:",1)

old='for x in cs:b+=\'<tr><td>\'+x["id"]+\'</td><td>\'+html.escape(x["version"] or "")+\'</td><td>\'+x["stage"]+\'</td><td>\'+x["state"]+\'</td><td>\'+html.escape(x["detail"])+\'</td></tr>\''
new="""for x in cs:
  ar=x["state"] in ("B_RUNNING","B_REVIEW","WAITING_FOR_B","READY_FOR_C","C_RUNNING","D_RUNNING","E_RUNNING","SYSTEM_HOLD","GOVERNANCE_HOLD")
  rowcls=' class="candidate-active"' if ar else ""
  badge='<span class="active-badge">ACTIVE · HUMAN ACTION REQUIRED</span> ' if x["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else ('<span class="active-badge">ACTIVE</span> ' if ar else "")
  b+='<tr'+rowcls+'><td>'+badge+x["id"]+'</td><td>'+html.escape(x["version"] or "")+'</td><td>'+x["stage"]+'</td><td>'+x["state"]+'</td><td>'+html.escape(x["detail"])+'</td></tr>'"""
if "candidate-active" not in s:
    if old not in s: raise SystemExit("HOLD: candidate row marker not found")
    s=s.replace(old,new,1)

cssneedle='pre{white-space:pre-wrap;background:#f8fafc;padding:12px}"'
cssadd='pre{white-space:pre-wrap;background:#f8fafc;padding:12px}.journey{display:grid;gap:10px}.journey-card{border:1px solid #d1d5db;border-radius:10px;padding:14px}.journey-card.done{background:#f0fdf4}.journey-card.active{border:2px solid #2563eb;background:#eff6ff}.journey-card.future{background:#f3f4f6;color:#6b7280}.journey-head{display:flex;gap:12px;align-items:center}.stage-letter{display:inline-flex;width:42px;height:42px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:700;font-size:20px}.future .stage-letter{background:#9ca3af}.state{font-size:13px;margin-top:3px;font-weight:700}.arrow{text-align:center;font-size:22px;color:#6b7280}.muted{color:#6b7280}.candidate-active{background:#eff6ff}.active-badge{display:inline-block;font-size:11px;font-weight:700;padding:3px 6px;border-radius:10px;background:#2563eb;color:white;margin-right:5px}"'
if ".journey-card" not in s:
    if cssneedle not in s: raise SystemExit("HOLD: CSS marker not found")
    s=s.replace(cssneedle,cssadd,1)

tmp=Path("gate2.fulljourney.tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
print("OPERATOR_FULL_JOURNEY_V1_2_APPLIED")
