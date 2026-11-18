import unittest,re
from bandgap_task import Task
class BandgapTests(unittest.TestCase):
 def test_paper_seed_exact_and_micron_render(self):
  t=Task();s=t.paper_design();self.assertAlmostEqual(s['NPTAT_w'],75.13e-6);self.assertEqual(t.decks(s)['nominal'],(t.templates/'nominal.scs').read_text())
 def test_m5_ratio_width_and_diffusion_follow_sizing(self):
  t=Task();d=t.paper_design();d['NPTAT_w']*=1.1;s=t.decks(d)['nominal']
  for name in ['M4']+['M5_'+str(i) for i in range(1,11)]:
   line=re.search(r'^\s*'+name+r' \([^\n]+',s,re.M)[0];v=dict(re.findall(r'(\w+)=(\S+)',line));self.assertAlmostEqual(float(v['w']),75.13*1.1);self.assertAlmostEqual(float(v['ad']),75.13*1.1*.29);self.assertEqual(v['mult'],'1')
  self.assertIn('parameters VS=1.8',s);self.assertIn('section=tt',s)
 def test_missing_results_never_fabricated(self):
  v,d=Task().extract({});self.assertTrue(all(x is None for x in v.values()))
if __name__=='__main__':unittest.main()
