import tempfile,unittest,subprocess,signal
from pathlib import Path
from unittest.mock import patch,MagicMock
import engine
class TimeoutTests(unittest.TestCase):
 def test_terminate_escalates_with_bounded_wait(self):
  p=MagicMock();p.pid=12345;p.wait.side_effect=[subprocess.TimeoutExpired('spectre',1),subprocess.TimeoutExpired('spectre',5),0]
  with tempfile.TemporaryDirectory() as d,patch.object(engine.subprocess,'Popen',return_value=p),patch.object(engine.os,'killpg') as kill:
   self.assertEqual(engine.execute('simulator lang=spectre',Path(d),timeout=1),124)
   self.assertEqual([c.args[1] for c in kill.call_args_list],[signal.SIGTERM,signal.SIGKILL])
   self.assertTrue(all('timeout' in c.kwargs for c in p.wait.call_args_list))
if __name__=='__main__':unittest.main()
