"""One regression group for actual fail-closed B boundary and historical ledger."""
import json,sqlite3,tempfile,unittest
from pathlib import Path
from b_operational_boundary import inspect
class BoundaryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.c=sqlite3.connect(":memory:")
  self.c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,created_at TEXT);
INSERT INTO candidates VALUES('CAND-B-002','RES-XAUUSD','C_STAGE1_REVIEW_REQUIRED','v2.1.3');
INSERT INTO decisions VALUES('DEC-F34D70261D','RES-XAUUSD','CAND-B-002','RELEASE_TO_C','2026-10-17T00:08:04Z');
INSERT INTO candidates VALUES('CAND-B-004','RES-XAUUSD','B_REVIEW','v1');""")
 def tearDown(self):self.c.close();self.tmp.cleanup()
 def test_historical_release_never_reissued(self):
  result=inspect(self.c,"CAND-B-002","RES-XAUUSD","v2.1.3",self.root)
  self.assertFalse(result["release_authorized"])
  self.assertIn("T09_CANDIDATE_ALREADY_RELEASED",result["failures"])
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],1)
 def test_new_candidate_without_operational_evidence_holds(self):
  result=inspect(self.c,"CAND-B-004","RES-XAUUSD","v1",self.root)
  self.assertEqual(result["state"],"GOVERNANCE_HOLD")
  self.assertIn("T04_EVIDENCE_MISSING",result["failures"])
 def test_synthetic_pass_does_not_grant_live_release(self):
  for filename in ("w6_live_input_readiness.json","w10_c_dependency_static_result.json",
                   "w6_t09_commission_ledger_result.json","w6_t10_policy_change_result.json"):
   (self.root/filename).write_text(json.dumps({"verdict":"PASS","evidence_class":"SYNTHETIC_TEST"}))
  result=inspect(self.c,"CAND-B-004","RES-XAUUSD","v1",self.root)
  self.assertFalse(result["release_authorized"])
  self.assertIn("ACTIVE_RELEASE_AUTHORITY_NOT_ESTABLISHED",result["failures"])
 def test_fourth_candidate_holds(self):
  self.c.executemany("INSERT INTO decisions VALUES(?,?,?,?,?)",[
   ("D2","RES-XAUUSD","CAND-B-005","RELEASE_TO_C","t2"),
   ("D3","RES-XAUUSD","CAND-B-006","RELEASE_TO_C","t3")])
  result=inspect(self.c,"CAND-B-004","RES-XAUUSD","v1",self.root)
  self.assertIn("T09_COMMISSION_LIMIT",result["failures"])
if __name__=="__main__":unittest.main()
