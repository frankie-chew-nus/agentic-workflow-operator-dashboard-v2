"""A-E workflow contract and actual dashboard safety regression."""
import unittest
from pathlib import Path
from workflow_matrix import allowed,commissioning,PROD,TEST
from b_operational_boundary import inspect
import sqlite3,tempfile
ROOT=Path(__file__).resolve().parent
class AEContractTests(unittest.TestCase):
 def test_stage1_review_cannot_advance_to_d(self):
  ok,reason=allowed("C","D","C_STAGE1_REVIEW_REQUIRED",PROD)
  self.assertFalse(ok);self.assertEqual(reason,"STATE_HOLD")
 def test_sandbox_d_cannot_advance_to_e(self):
  ok,reason=allowed("D","E","D_OOS_PASS",TEST)
  self.assertFalse(ok);self.assertEqual(reason,"EVIDENCE_KIND_HOLD")
 def test_incomplete_provenance_blocks_commissioning(self):
  chain=[{"stage":stage,"kind":PROD,"hash_ok":True,"identity":True,"state":state}
   for stage,state in zip(("A","B","C","D"),("A_PASS","READY_FOR_C","C_STAGE1_REVIEW_REQUIRED","D_OOS_PASS"))]
  self.assertEqual(commissioning(chain),(False,"STATE_HOLD"))
 def test_unverified_hash_blocks_transition(self):
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,hash_ok=False),(False,"HASH_HOLD"))
 def test_no_human_authority_blocks_transition(self):
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,human=False),(False,"HUMAN_AUTHORITY_HOLD"))
 def test_actual_dashboard_release_handler_is_inspected(self):
  source=(ROOT/"gate2.py").read_text(encoding="utf-8")
  self.assertIn("from b_operational_boundary import inspect",source)
  self.assertIn("if review['release_authorized']:",source)
  self.assertNotIn("elif d=='RELEASE_TO_C':decision(",source)
 def test_historical_release_is_not_mutated_by_inspection(self):
  with tempfile.TemporaryDirectory() as td:
   c=sqlite3.connect(":memory:")
   try:
    c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,created_at TEXT);
INSERT INTO candidates VALUES('CAND-B-002','RES-XAUUSD','C_STAGE1_REVIEW_REQUIRED','v2.1.3');
INSERT INTO decisions VALUES('DEC-F34D70261D','RES-XAUUSD','CAND-B-002','RELEASE_TO_C','2026-10-17');""")
    before=list(c.execute("SELECT * FROM decisions"))
    result=inspect(c,"CAND-B-002","RES-XAUUSD","v2.1.3",Path(td))
    self.assertFalse(result["release_authorized"])
    self.assertEqual(before,list(c.execute("SELECT * FROM decisions")))
   finally:c.close()
if __name__=="__main__":unittest.main()
