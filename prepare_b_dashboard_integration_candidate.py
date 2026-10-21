"""Build an isolated, reviewable active-dashboard integration candidate.

Never overwrites gate2.py or opens active SQLite databases. Output is a
candidate file, not an activated dashboard. Its fixture-dependent authority
remains test-only; do not deploy it to active use.
"""
import argparse,hashlib,json
from pathlib import Path
from build_disposable_pin_dashboard_integrated import build
ROOT=Path(__file__).resolve().parent
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--output-root",required=True)
 args=parser.parse_args()
 root=Path(args.output_root).resolve()
 if root==ROOT or ROOT in root.parents:raise SystemExit("OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")
 target=root/"w6_disposable_dashboard"/"gate2.py"
 source=ROOT/"gate2.py"
 if target.exists():raise SystemExit("REFUSE_OVERWRITE_EXISTING_CANDIDATE")
 build(source,target)
 original=source.read_bytes();candidate=target.read_bytes()
 manifest={"status":"REVIEW_ONLY_NOT_ACTIVATED",
  "source":str(source),"candidate":str(target),
  "source_sha256":hashlib.sha256(original).hexdigest(),
  "candidate_sha256":hashlib.sha256(candidate).hexdigest(),
  "source_unchanged":hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(original).digest(),
  "active_database_accessed":False,
  "blocking_issues":["test-only authority fixture","real governance evidence not verified",
                     "PIN credential provisioning not integrated","rollback drill not verified"]}
 (root/"candidate_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
 print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
