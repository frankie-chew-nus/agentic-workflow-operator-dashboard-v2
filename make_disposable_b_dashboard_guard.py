"""Generate a fail-closed disposable copy of dashboard gate2.py.

Never writes to active gate2.py. No production activation or authority binding.
The inserted guard rejects RELEASE_TO_C before the decision insert/state update.
"""
from pathlib import Path
import shutil

ORIGINAL="elif d=='RELEASE_TO_C':decision(c,r['id'],cid,d,rat);c.execute(\"UPDATE candidates SET state='READY_FOR_C',stage='B',detail='Human released corrected B candidate to C queue' WHERE id=?\",(cid,))"
REPLACEMENT="""elif d=='RELEASE_TO_C':
                # Experimental fail-closed guard: no trusted live binding exists.
                from b_release_guard_candidate import release_preflight
                gate=release_preflight(candidate_id=cid,research_id=r['id'],verified_context=None)
                if gate['release_authorized']:
                    raise RuntimeError('UNEXPECTED_RELEASE_AUTHORITY')
                c.execute("UPDATE candidates SET detail=? WHERE id=?",('B release blocked: '+','.join(gate['failures']),cid))"""

def make_disposable_copy(source, destination):
 source=Path(source).resolve()
 destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard":
  raise ValueError("Destination must be inside w6_disposable_dashboard")
 if source==destination or not source.is_file():
  raise ValueError("Invalid source/destination")
 text=source.read_text(encoding="utf-8")
 if text.count(ORIGINAL)!=1:
  raise ValueError("Release branch mismatch: fail closed; review source")
 modified=text.replace(ORIGINAL,REPLACEMENT)
 compile(modified,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(modified,encoding="utf-8")
 return destination
