"""Bind four frozen nominal judges to curator's existing real-LLM LEDRO adapter."""
from pathlib import Path
import sys
P=Path(__file__).resolve().parent;A=P.parents[3]
sys.path.insert(0,str(A/'src'));sys.path.insert(0,str(A/'sizing'))
from judge import SizingProblem
from ledro_adapter import run
run.SizingProblem=SizingProblem
BaseRun=run.Run
class CheckpointRun(BaseRun):
 def f_batch(self,X):
  values=[]
  for start in range(0,len(X),max(1,self.a.jobs)):
   values.extend(super().f_batch(X[start:start+max(1,self.a.jobs)]))
   self._write('best_so_far.json',self.best())
  return values
run.Run=CheckpointRun
if __name__=='__main__':run.main()
