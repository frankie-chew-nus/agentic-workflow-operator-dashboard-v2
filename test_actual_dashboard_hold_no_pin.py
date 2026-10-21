"""Regression for the actual gate2.py B->C HOLD-only handler.

Uses disposable HTTP/SQLite and does not modify the active dashboard DB.
Historical C-stage candidate is not re-released.
"""
import importlib.util,shutil,sqlite3,sys,tempfile,threading,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
class ActualHoldOnlyTests(unittest.TestCase):
 def test_actual_dashboard_blocks_release_and_preserves_ledger(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td);shutil.copy2(ROOT/"gate2.py",base/"gate2.py")
   for name in ("operator_artifacts.py","operator_paths.json","b_operational_boundary.py"):shutil.copy2(ROOT/name,base/name)
   saved={name:sys.modules.pop(name,None) for name in ("operator_artifacts","b_operational_boundary")};sys.path.insert(0,str(base))
   server=None;worker=None
   try:
    spec=importlib.util.spec_from_file_location("actual_hold_gate2",base/"gate2.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.init()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    server.daemon_threads=False
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C",
     "rationale":"Human requested release; operational evidence still on HOLD"}).encode()
    with urllib.request.urlopen(urllib.request.Request(
      f"http://127.0.0.1:{server.server_address[1]}/",data=data),timeout=5) as response:
     self.assertEqual(response.status,200)
    c=sqlite3.connect(module.DB)
    try:
     self.assertEqual(c.execute("SELECT state FROM candidates WHERE id='CAND-B-002'").fetchone()[0],"B_REVIEW")
     self.assertEqual(c.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0],0)
     self.assertIn("governance HOLD",c.execute("SELECT detail FROM candidates WHERE id='CAND-B-002'").fetchone()[0])
    finally:c.close()
   finally:
    if server:
     server.shutdown();server.server_close()
     if worker:worker.join(timeout=5)
    sys.path.remove(str(base))
    for name,original in saved.items():
     sys.modules.pop(name,None)
     if original is not None:sys.modules[name]=original
if __name__=="__main__":unittest.main()
