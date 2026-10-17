import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import core
class ContractTests(unittest.TestCase):
 def test_ohlc_and_friction(self):
  bars=[{"timestamp":f"2026-01-01T00:{i:02}:00","open":100.,"high":102.,"low":98.,"close":101.} for i in range(30)]
  out=core.simulate(bars,lambda h,p:1,{})
  self.assertEqual(out["trade_count"],4)
  self.assertAlmostEqual(out["trades"][0]["pnl_after_friction"],.91)
 def test_invalid_signal_fails_closed(self):
  bars=[{"timestamp":f"2026-01-01T00:{i:02}:00","open":100.,"high":102.,"low":98.,"close":101.} for i in range(30)]
  with self.assertRaisesRegex(ValueError,"INVALID_SIGNAL"):core.simulate(bars,lambda h,p:2,{})
 def test_artifact_tampering_detected(self):
  with tempfile.TemporaryDirectory() as tmp:
   old=core.ROOT;core.ROOT=Path(tmp)
   try:
    rid=core.new("Synthetic test");c=core.db()
    with c:p=core.artifact(c,rid,"A","research",{"sources":[1]})
    p.write_text('{"sources":[]}',encoding="utf-8")
    with self.assertRaisesRegex(ValueError,"TAMPERED"):core.read_artifact(c,rid,"A","research")
    c.close()
   finally:core.ROOT=old
 def test_diagnostic_cannot_commission(self):
  with tempfile.TemporaryDirectory() as tmp:
   old=core.ROOT;core.ROOT=Path(tmp)
   try:
    rid=core.new("Synthetic");c=core.db()
    with c:
     core.artifact(c,rid,"D","oos",{"qualified":False});core.state(c,rid,"E","WAIT_HUMAN","Synthetic")
    c.close()
    with self.assertRaisesRegex(ValueError,"COMMISSION_BLOCKED"):core.approve(rid,"APPROVE","human evidence review")
   finally:core.ROOT=old
if __name__=="__main__":unittest.main()
