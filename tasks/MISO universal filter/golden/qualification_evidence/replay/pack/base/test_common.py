import unittest,math,tempfile
from pathlib import Path
from unittest.mock import patch
from judge import score_constraints,validate_design,SizingProblem
class SafetyTests(unittest.TestCase):
 def test_missing_nan_and_boolean_fail(self):
  specs=[dict(name=n,lower=9,upper=11,paper_value=10) for n in ['missing','nan','bool','ok']]
  out=score_constraints(specs,dict(nan=float('nan'),bool=True,ok=10))
  self.assertEqual(sum(c['passed'] for c in out.values()),1)
  self.assertTrue(all(out[n]['value'] is None for n in ['missing','nan','bool']))
 def test_negative_target_and_upper_limit(self):
  s=[dict(name='db',lower=-26.4,upper=-21.6,paper_value=-24),dict(name='thd',lower=0,upper=6,paper_value=6)]
  a=score_constraints(s,dict(db=-24,thd=.1));self.assertTrue(all(c['passed'] for c in a.values()))
  self.assertFalse(score_constraints(s,dict(db=-20,thd=7))['db']['passed'])
 def test_paper_strict_upper_limit(self):
  s=[dict(name='thd',lower=0,upper=6,paper_value=6,upper_exclusive=True)]
  self.assertFalse(score_constraints(s,dict(thd=6))['thd']['passed'])
  self.assertTrue(score_constraints(s,dict(thd=5.99))['thd']['passed'])
 def test_invalid_seed_not_silently_clipped(self):
  v=[dict(name='w',lower=1,upper=3)]
  for d in [{},{'w':0},{'w':float('nan')},{'w':2,'extra':1}]:
   with self.assertRaises(ValueError):validate_design(v,d)
  validate_design(v,dict(w=2))
if __name__=='__main__':unittest.main()
