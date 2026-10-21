from pathlib import Path
import py_compile
p=Path("gate2.py"); s=p.read_text(encoding="utf-8"); bak=Path("gate2.pre_current_step_v1_3.py")
if bak.exists(): raise SystemExit("HOLD: backup already exists")

# Move the existing B review controls into the B journey card by capturing the action card HTML.
# We do this with a small post-render transform: identify the standalone ACTION REQUIRED card,
# remove it, then inject its inner content into the active B journey section.
needle='return "<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>"'
if needle not in s: raise SystemExit("HOLD: final render marker not found")
replacement=r"""# v1.3: integrate current Human action into the active B journey card.
 # The existing action renderer remains authoritative; only presentation changes.
 if 'ACTION REQUIRED — HUMAN B→C REVIEW' in b:
  import re
  m=re.search(r'(<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b>.*?</div>)(?=<div class=card><h2>Candidate pipeline)',b,re.S)
  if m:
   action=m.group(1)
   # remove outer card wrapper so controls live inside current B stage
   inner=action.replace('<div class="card action">','<div class="embedded-action">',1)
   # remove standalone card
   b=b[:m.start()]+b[m.end():]
   # inject before closing active B section; active journey B is the only active section at this stage
   marker='</section><div class="arrow">↓</div><section class="journey-card future">'
   if marker in b:
    b=b.replace(marker,inner+'</div></section><div class="arrow">↓</div><section class="journey-card future">',1)
 return "<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>"""
s=s.replace(needle,replacement,1)

# Improve expandable evidence presentation and embedded action styling.
cssneedle='pre{white-space:pre-wrap;background:#f8fafc;padding:12px}'
if cssneedle not in s: raise SystemExit("HOLD: CSS marker not found")
cssnew='pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto;border:1px solid #d1d5db;border-radius:8px}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}details summary{cursor:pointer;font-weight:700;color:#1d4ed8}.embedded-action{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.embedded-action h2{margin-top:8px}'
s=s.replace(cssneedle,cssnew,1)

tmp=Path("gate2.v13tmp.py");tmp.write_text(s,encoding="utf-8");py_compile.compile(str(tmp),doraise=True)
bak.write_text(p.read_text(encoding="utf-8"),encoding="utf-8");p.write_text(s,encoding="utf-8");tmp.unlink()
print("OPERATOR_CURRENT_STEP_V1_3_APPLIED")
