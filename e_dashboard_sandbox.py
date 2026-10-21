"""Dashboard-safe E sandbox adapter using only D workflow-test evidence."""
import json
from pathlib import Path
from operator_handoff import TEST,envelope
from e_sandbox import audit
def execute(root,d_root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);d_root=Path(d_root)
 ds=d_root/"d_output"/"d_summary.json"
 if not ds.exists():
  x={"state":"E_SANDBOX_HOLD","reason":"D_SANDBOX_EVIDENCE_MISSING","commissioning_authority":False,"commissioned":False};(root/"dashboard_summary.json").write_text(json.dumps(x,indent=2));return x
 h=envelope("D","FIX-D-001","v0",TEST,[("d_summary",ds)],"D_SANDBOX_PASS")
 x=audit(h,["D_SANDBOX_REVIEW"],["D_SANDBOX_REVIEW"],root/"e_audit.json")
 (root/"dashboard_summary.json").write_text(json.dumps(x,indent=2));return x
