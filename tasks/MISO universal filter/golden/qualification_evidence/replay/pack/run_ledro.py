"""Private all-corner LEDRO binding; shared adapter untouched."""
from pathlib import Path
import sys,datetime,subprocess,json
P=Path(__file__).resolve().parent
sys.path.insert(0,'<ANALOGIQ>/src');sys.path.insert(0,'<ANALOGIQ>/sizing')
from corner_judge import SizingProblem
from ledro_adapter import run
run.SizingProblem=SizingProblem
# A transient CLI failure must use the adapter's documented LLMError recovery path.
_original_ask=run.llm_mod.ClaudeCLI.ask
def bounded_ask(self,system,prompt):
 try:return _original_ask(self,system,prompt)
 except (subprocess.TimeoutExpired,OSError) as exc:raise run.llm_mod.LLMError(type(exc).__name__+': '+str(exc)) from exc
run.llm_mod.ClaudeCLI.ask=bounded_ask
_original_score=run.score
def strict_score(metrics,weights,obj_weight,obj_scale,names=None):
 result=_original_score(metrics,weights,obj_weight,obj_scale,names=names)
 for name,c in ((metrics or {}).get('constraints') or {}).items():
  if c.get('passed') is False and result['shortfalls'].get(name,0)==0:
   penalty=weights.get(name,1.0)*1e-6
   result['shortfalls'][name]=penalty;result['f']+=penalty
 result['reward']=-result['f']
 return result
run.score=strict_score
run.REWARD_DOCS['ledro']+=' Every scalar is aggregated at its worst corner; strict-bound equality failure has a small positive penalty. Bandgap startup is a required constraint; DTMOS gain interpretation is branch-specific and other physical qualifications remain explicit.'
_original_system_prompt=run.P.system_prompt
def exact_system_prompt(problem,dut_text,reward_doc):
 lines=_original_system_prompt(problem,dut_text,reward_doc).splitlines()
 for c in problem['constraints']:
  for i,line in enumerate(lines):
   if line.startswith('- '+c['name']+' '):
    if c.get('upper_exclusive'):line=line.replace('<=','<')
    if c.get('lower_exclusive'):line=line.replace('>=','>')
    lines[i]=line
 return '\n'.join(lines)
run.P.system_prompt=exact_system_prompt
BaseRun=run.Run
class CornerRun(BaseRun):
 def __init__(self,args):
  super().__init__(args)
  self.meta.update(corner_count=len(self.problem['conditions']),metric_count=len(self.problem['constraints']),aggregation='worst normalized bound margin across all configured corners',start_kind='best saved sizing',search_deadline_utc=datetime.datetime.fromtimestamp(self.deadline,datetime.timezone.utc).isoformat() if self.deadline else None,physical_feasibility='Retainedscalar targetfeasibility only; startup/shape/bias diagnostics separately qualified')
  self.meta.update(gmc_excluded=True,physical_feasibility='Bandgap includes mandatory startup qualification; DTMOS gain branches have explicitly different interpretation; unresolved physical limitations remain documented')
  self._write('meta.json',self.meta)
 def _evaluate_one(self,design,eid):
  rec=super()._evaluate_one(design,eid);flat=rec.get('_flat') or {}
  rec['corner_summary']=(flat.get('diagnostics') or {}).get('corner_summary');rec['targets_met']=flat.get('targets_met');rec['targets']=flat.get('targets')
  return rec
 def run(self):
  summary=super().run()
  p=self.out/'verify_sim/metrics.json'
  if p.exists():
   flat=json.loads(p.read_text());v=json.loads((self.out/'verify.json').read_text());v['corner_summary']=flat.get('diagnostics',{}).get('corner_summary');v['feasibility_scope']=flat.get('feasibility_scope');v['physical_diagnostics_file']=str(p);self._write('verify.json',v)
  coverage=self.coverage_best()
  if coverage and self.best() and coverage['eval']!=self.best()['eval']:
   sp=SizingProblem(self.a.task+'_full')
   flat=sp.evaluate(coverage['params'],self.out/'coverage_verify_sim',keep_raw=True)
   self._write('coverage_verify.json',{'source_eval':coverage['eval'],'feasible':flat['feasible'],'corner_summary':flat['diagnostics']['corner_summary'],'execution_status':flat['execution_status']})
  return summary
 def coverage_best(self):
  good=[h for h in self.history if h.get('execution')=='completed' and h.get('corner_summary')]
  return max(good,key=lambda h:(bool(h.get('feasible')),h['corner_summary']['all_metrics_pass_corners'],h['corner_summary']['scalar_passes'],-h['f']),default=None)
 def f_batch(self,X):
  values=[]
  for i in range(0,len(X),max(1,self.a.jobs)):
   values.extend(super().f_batch(X[i:i+max(1,self.a.jobs)]));self._write('best_so_far.json',self.best());self._write('best_coverage_so_far.json',self.coverage_best())
   good=[h for h in self.history if h.get('execution')=='completed' and h.get('corner_summary')]
   if good:self._write('best_scalar_so_far.json',max(good,key=lambda h:(h['corner_summary']['scalar_passes'],-h['f'])))
  return values
run.Run=CornerRun
if __name__=='__main__':run.main()
