"""Build a fail-closed dashboard copy; never alters active gate2.py.

RELEASE_TO_C is unconditionally blocked regardless of PIN, config or manifest.
Preserves all other dashboard actions. This is a review/acceptance artifact.
"""
from pathlib import Path
from make_disposable_b_dashboard_guard import ORIGINAL
REPLACEMENT="""elif d=='RELEASE_TO_C':
                c.execute("UPDATE candidates SET detail=? WHERE id=?",
                          ('B governance HOLD: release disabled pending T04/T05/T09/T10 operational verification',cid))"""
def build(source,destination):
 source=Path(source).resolve(strict=True);destination=Path(destination).resolve()
 if source==destination or destination.parent.name!="w6_disposable_dashboard":
  raise ValueError("ISOLATED_DESTINATION_REQUIRED")
 original=source.read_text(encoding="utf-8")
 if original.count(ORIGINAL)!=1:raise ValueError("RELEASE_BRANCH_CHANGED")
 modified=original.replace(ORIGINAL,REPLACEMENT)
 compile(modified,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 if destination.exists():raise FileExistsError("REFUSE_OVERWRITE")
 destination.write_text(modified,encoding="utf-8")
 return destination
