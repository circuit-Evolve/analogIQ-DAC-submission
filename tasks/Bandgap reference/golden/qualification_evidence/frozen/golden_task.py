"""Frozen evaluator for the measured 15-corner bandgap candidate.
Only physical W/L and passive values change; original topology/models retained.
"""
from pathlib import Path
import sys,json,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'pack'))
from robust_bandgap import Task as Base
from bandgap_corners import _engine
from corner_judge import write,aggregate
EXTRA={'M4_w','M4_l','M13_w','M11_w'}
class GoldenTask(Base):
 def validate(self,d):
  base={v['name'] for v in self.variables};assert set(d) in (base,base|EXTRA),'Missing or unknown sizing key'
  Base.validate(self,{k:v for k,v in d.items() if k in base})
  for k,v in d.items():
   assert isinstance(v,(int,float)) and math.isfinite(v)
   if k.endswith('_w'):assert .42e-6<=v<=100e-6,(k,v)
   if k.endswith('_l'):assert .15e-6<=v<=20e-6,(k,v)
 def decks(self,d):
  assert set(d)=={v['name'] for v in self.variables}|EXTRA
  self.validate(d);plain={k:v for k,v in d.items() if k not in EXTRA};decks=super().decks(plain)
  updates={'bgr_fig3_paper':{'M4':{'w':d['M4_w']*1e6,'l':d['M4_l']*1e6},'M13':{'w':d['M13_w']*1e6},'M11':{'w':d['M11_w']*1e6}}}
  return {name:_engine.mutate(s,updates) for name,s in decks.items()}
def design():return json.loads((HERE/'candidate_design.json').read_text())['parameters']
def verify(task,out,d):
 result=task.evaluate(d,out,keep_raw=True,timeout=180);cons,counts,ok=aggregate(task.cfg['constraints'],task.conditions,result)
 flat={'design':d,'constraints':cons,'corner_summary':counts,'execution_ok':ok,'feasible':ok and all(c['passed'] for c in cons.values()),'diagnostics':result};write(Path(out)/'metrics.json',flat);return flat
