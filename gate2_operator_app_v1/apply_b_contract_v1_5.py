from pathlib import Path
import py_compile

p=Path("gate2.py")
if not p.exists(): raise SystemExit("HOLD: gate2.py not found")
s=p.read_text(encoding="utf-8")
bak=Path("gate2.pre_b_contract_v1_5.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

helper = '''
def b_contract_result():
    hold=BASE/'evidence'/'b_resume'/'CAND-B-002'/'b_regression_hold.json'
    attempted=BASE/'evidence'/'b_resume'/'CAND-B-002'/'corrected_candidate.json'
    previous=BASE/'evidence'/'b_resume'/'CAND-B-002'/'b_corrected_release.json'
    contract=BASE/'b002_revision_contract.json'
    def load(p):
        try: return json.load(open(p,encoding='utf-8')) if p.exists() else None
        except: return None
    return load(contract),load(hold),load(previous),load(attempted)

def governance_hold_html():
    contract,hold,previous,attempted=b_contract_result()
    if not hold or hold.get('reason')!='CORRECTION_REGRESSION': return ''
    fails=hold.get('failures',[])
    mapping={
      'VERSION_MUST_BE':'VERSION','STRICT_NR_N_NOT_PRESERVED':'STRICT_NR_N',
      'VOLATILITY_EXPANSION_RULE_MISSING':'VOL_RULE','VOLATILITY_EXPANSION_NOT_IN_ENTRY':'VOL_ENTRY',
      'ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED':'ATR_DEFAULT'
    }
    failed_ids=set()
    for f in fails:
        key=f.split(':',1)[0]; failed_ids.add(mapping.get(key,key))
    rows=[]
    for r in (contract or {}).get('rules',[]):
        bad=r['id'] in failed_ids
        rows.append('<tr class="rule-fail"' if bad else '<tr class="rule-pass"')
        rows[-1]+='><td>'+('✗' if bad else '✓')+'</td><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['label'])+'</td></tr>'
    prevcand=(previous or {}).get('candidate',{})
    att=(attempted or {}); attcand=att.get('candidate',att) if isinstance(att,dict) else {}
    return '<div class="governance-panel"><h3>GOVERNANCE HOLD — CORRECTION REGRESSION</h3><p>The attempted B correction was blocked before release.</p><p><b>Parent version:</b> '+html.escape(str(hold.get('parent_version','')))+' &nbsp; <b>Attempted:</b> '+html.escape(str(hold.get('attempted_version','')))+'</p><h4>Revision contract</h4><table class="rules"><tr><th></th><th>Rule</th><th>Requirement</th></tr>'+''.join(rows)+'</table><details><summary>View previous valid specification</summary><pre>'+html.escape(json.dumps(prevcand,indent=2))+'</pre></details><details><summary>View attempted specification</summary><pre>'+html.escape(json.dumps(attcand,indent=2))+'</pre></details><details><summary>View raw failed-rule evidence</summary><pre>'+html.escape(json.dumps(hold,indent=2))+'</pre></details></div>'
'''

if "def b_contract_result(" not in s:
    marker="def render():"
    if marker not in s: raise SystemExit("HOLD: render marker not found")
    s=s.replace(marker,helper+"\n"+marker,1)

# Translate completed B governance regression from generic SYSTEM_HOLD in dispatcher.
old='''else:c.execute("UPDATE candidates SET state='SYSTEM_HOLD',detail=? WHERE id=?",("B workflow failed. View "+j["log_path"],j["candidate_id"]))'''
new='''else:
   gh=BASE/"evidence"/"b_resume"/j["candidate_id"]/"b_regression_hold.json"
   if gh.exists():
    try:
     gx=json.load(open(gh,encoding="utf-8"))
    except: gx={}
   else: gx={}
   if gx.get("reason")=="CORRECTION_REGRESSION":
    c.execute("UPDATE candidates SET state='GOVERNANCE_HOLD',detail=? WHERE id=?",("Correction regression blocked. Review failed B revision contract rules.",j["candidate_id"]))
   else:
    c.execute("UPDATE candidates SET state='SYSTEM_HOLD',detail=? WHERE id=?",("B workflow failed. View "+j["log_path"],j["candidate_id"]))'''
if "Correction regression blocked." not in s:
    if old not in s: raise SystemExit("HOLD: dispatcher failure renderer not found")
    s=s.replace(old,new,1)

# Add GOVERNANCE_HOLD operating card branch immediately before SYSTEM_HOLD.
needle='elif x and x["state"]=="SYSTEM_HOLD":'
branch='''elif x and x["state"]=="GOVERNANCE_HOLD":
   b+='<div class="card hold"><b>ACTION REQUIRED — GOVERNANCE HOLD</b><h2>CAND-B-002</h2>'+governance_hold_html()+'<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="Human rationale / additional instruction"></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RETURN_FAILED_RULES>Return to B with failed rules</button><button class=bad name=decision value=REJECT>Reject candidate</button></form></div>'
  '''
if "RETURN_FAILED_RULES" not in s:
    if needle not in s: raise SystemExit("HOLD: SYSTEM_HOLD branch not found")
    s=s.replace(needle,branch+needle,1)

# Route Return-with-failed-rules through same governed B job; checker evidence is already in work package artifacts.
olddec='if d in ("RETURN_TO_B","RESUME_B","RETRY_B"):'
newdec='if d in ("RETURN_TO_B","RESUME_B","RETRY_B","RETURN_FAILED_RULES"):'
if "RETURN_FAILED_RULES\"):" not in s:
    if olddec not in s: raise SystemExit("HOLD: B decision route not found")
    s=s.replace(olddec,newdec,1)

# CSS for friendly contract table.
css_anchor=".hold-inline{border-left:5px solid #d97706;padding-left:14px}"
css_more=css_anchor+".governance-panel{margin:12px 0}.rules td,.rules th{font-size:14px}.rule-pass{background:#f0fdf4}.rule-fail{background:#fef2f2;font-weight:600}.rule-pass td:first-child{color:#15803d}.rule-fail td:first-child{color:#b91c1c}"
if ".governance-panel{" not in s:
    if css_anchor not in s: raise SystemExit("HOLD: CSS anchor not found")
    s=s.replace(css_anchor,css_more,1)

tmp=Path("gate2.v15tmp.py")
tmp.write_text(s,encoding="utf-8")
py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
tmp.unlink()
print("OPERATOR_B_CONTRACT_V1_5_APPLIED")
