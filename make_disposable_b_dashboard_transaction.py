"""Disposable actual gate2.py handler patch for transactional B->C release.

No active file modifications. Mock verifier only through an explicit disposable
test module; absent fixture means HOLD. Existing gate2.py connection must commit
only after the transaction completes; no second decision insertion.
"""
from pathlib import Path
from make_disposable_b_dashboard_guard import ORIGINAL

REPLACEMENT="""elif d=='RELEASE_TO_C':
                from b_disposable_release_transaction import attempt
                from b_disposable_authority_fixture import context_for, verify
                gate=attempt(c,cid,r['id'],context_for(cid,r['id']),verify,disposable=True)
                if gate['state']!='DISPOSABLE_RELEASED':
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",('B governance HOLD: '+gate.get('reason','UNKNOWN'),cid))"""

def make_transaction_copy(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard" or source==destination:
  raise ValueError("DISPOSABLE_PATH_REQUIRED")
 code=source.read_text(encoding="utf-8")
 if code.count(ORIGINAL)!=1:raise ValueError("RELEASE_BRANCH_CHANGED")
 patched=code.replace(ORIGINAL,REPLACEMENT)
 compile(patched,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(patched,encoding="utf-8")
 return destination
