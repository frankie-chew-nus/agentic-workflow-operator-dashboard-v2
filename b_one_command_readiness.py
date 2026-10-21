"""One-command B->C readiness audit. READ ONLY to active dashboard and DB.

Checks local PIN configuration, real evidence hashes, backup integrity, and
builds an isolated dashboard copy. Never enables approval or patches gate2.py.
"""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from build_local_pin_dashboard_candidate import build
from b_local_operator_release import check_evidence
from verify_b_rollback_readonly import check as check_backup
ROOT=Path(__file__).resolve().parent
def latest_backup(root):
 candidates=sorted((root/"Gate2_Evidence"/"W6_GOVERNANCE_ROLLBACK_BACKUPS").glob("*/backup_manifest.json"),reverse=True)
 return candidates[0].parent if candidates else None
def run():
 p=argparse.ArgumentParser()
 p.add_argument("--config",default=str(Path.home()/"MSI5002_Local_Approval"/"local_approval_config.json"))
 p.add_argument("--backup-dir",default=None)
 a=p.parse_args()
 results={}
 active=ROOT/"gate2.py";original=hashlib.sha256(active.read_bytes()).hexdigest()
 config=Path(a.config)
 try:
  cfg=json.loads(config.read_text(encoding="utf-8"))
  manifest=Path(cfg["evidence_manifest"])
  m=json.loads(manifest.read_text(encoding="utf-8"))
  results["local_pin_enrolled"]=isinstance(cfg.get("pin_record"),dict) and bool(cfg["pin_record"].get("digest"))
  results["release_enabled"]=cfg.get("enabled") is True
  results["governance_evidence"]=check_evidence(m.get("candidate_id"),m.get("candidate_version"),m.get("research_id"),manifest) or "PASS"
 except Exception as e:
  results["local_pin_enrolled"]=False
  results["release_enabled"]=False
  results["governance_evidence"]="CONFIG_OR_MANIFEST_INVALID:"+type(e).__name__
 backup=Path(a.backup_dir) if a.backup_dir else latest_backup(ROOT.parent)
 if backup:
  try:results["backup"]=check_backup(backup)
  except Exception as e:results["backup"]={"status":"FAIL","reason":type(e).__name__}
 else:results["backup"]={"status":"MISSING"}
 with tempfile.TemporaryDirectory() as td:
  destination=Path(td)/"w6_disposable_dashboard"/"gate2.py"
  try:
   build(active,destination)
   candidate=destination.read_text(encoding="utf-8")
   results["isolated_dashboard_build"]="PASS" if "b_local_operator_release import release" in candidate and 'name="pin"' in candidate else "FAIL"
  except Exception as e:results["isolated_dashboard_build"]="FAIL:"+type(e).__name__
 results["active_dashboard_unchanged"]=hashlib.sha256(active.read_bytes()).hexdigest()==original
 results["active_dashboard_hash"]=original
 results["activation_authorized"]=False
 results["status"]="REVIEW_REQUIRED_NO_ACTIVATION"
 print(json.dumps(results,indent=2))
 return 0
if __name__=="__main__":sys.exit(run())
