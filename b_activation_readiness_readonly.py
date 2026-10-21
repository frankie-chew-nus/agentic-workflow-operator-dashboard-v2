"""Read-only activation readiness report. Never modifies dashboard or databases.

This deliberately reports BLOCKED while approval context is provided by a
simulated fixture and production authority remains unimplemented.
"""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REQUIRED=("gate2.py","build_disposable_pin_dashboard_integrated.py",
          "b_disposable_pin_atomic.py","b_disposable_pin_authority.py",
          "b_disposable_trusted_approval.py","test_integrated_disposable_pin_dashboard_http.py")
def report():
 missing=[name for name in REQUIRED if not (ROOT/name).is_file()]
 source=ROOT/"gate2.py"
 code=source.read_text(encoding="utf-8") if source.exists() else ""
 direct="elif d=='RELEASE_TO_C':decision(c,r['id'],cid,d,rat)" in code
 try:commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 except Exception:commit="UNKNOWN"
 checks={
  "required_files_present":not missing,
  "active_dashboard_still_has_unguarded_release":direct,
  "real_human_identity_verified":False,
  "production_approval_context_implemented":False,
  "atomic_pin_handler_active":False,
  "rollback_restore_drill_verified":False,
 }
 return {"status":"BLOCKED_NO_ACTIVATION","commit":commit,
         "active_dashboard_sha256":hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None,
         "checks":checks,"missing_files":missing,
         "next_actions":["Create non-simulated local approval enrollment and evidence binding",
          "Verify backup manifest and restore drill without changing active files",
          "Replace direct release only after explicit Human authorization"],
         "active_files_modified":False}
if __name__=="__main__":print(json.dumps(report(),indent=2))
