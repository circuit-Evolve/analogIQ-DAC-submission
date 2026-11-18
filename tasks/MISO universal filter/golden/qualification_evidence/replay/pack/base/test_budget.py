from types import SimpleNamespace
from unittest.mock import patch
import unittest
import run_ledro as wrapper
class BudgetTests(unittest.TestCase):
 def instance(self):
  x=object.__new__(wrapper.CheckpointRun);x.a=SimpleNamespace(jobs=2);x.saved=[];x._write=lambda n,v:x.saved.append(v);x.best=lambda:'checkpoint';return x
 def test_initial_population_deadline_checked_per_two_designs(self):
  batches=[];x=self.instance()
  def base(self,values):
   batches.append(list(values))
   if len(batches)==2:raise wrapper.run.TimeLimit('run')
   return list(values)
  with patch.object(wrapper.BaseRun,'f_batch',base):
   with self.assertRaises(wrapper.run.TimeLimit):x.f_batch(list(range(12)))
  self.assertEqual(batches,[[0,1],[2,3]]);self.assertEqual(x.saved,['checkpoint'])
 def test_output_order_and_complete_checkpointing(self):
  batches=[];x=self.instance()
  def base(self,values):batches.append(list(values));return [v*2 for v in values]
  with patch.object(wrapper.BaseRun,'f_batch',base):self.assertEqual(x.f_batch(list(range(5))),[0,2,4,6,8])
  self.assertEqual([len(b) for b in batches],[2,2,1]);self.assertEqual(len(x.saved),3)
if __name__=='__main__':unittest.main()
