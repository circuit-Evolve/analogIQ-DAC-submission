"""Real LEDRO interface: every metric must satisfy every configured corner."""
from pathlib import Path
from types import SimpleNamespace
import importlib,json,math,numbers
P=Path(__file__).resolve().parent
TASKS={'miso':'robust_miso','bandgap':'robust_bandgap','dtmos_gain200':'dtmos_gain200','dtmos_passband':'dtmos_passband'}
def write(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda x:float(x)));tmp.replace(path)
def finite(x):return isinstance(x,numbers.Real) and not isinstance(x,bool) and math.isfinite(x)
def validate(variables,design):
 if set(design)!={v['name'] for v in variables}:raise ValueError('Specify all sizing variables exactly')
 for v in variables:
  x=design[v['name']]
  if not finite(x) or not v['lower']<=x<=v['upper']:raise ValueError('Invalid/out-of-bounds '+v['name'])
def single(spec,value):
 v=float(value) if finite(value) else None;ms=[];scale=abs(spec.get('paper_value') or 1)
 if v is not None:
  if spec.get('lower') is not None:ms.append((v-spec['lower'])/scale)
  if spec.get('upper') is not None:ms.append((spec['upper']-v)/scale)
 passed=v is not None and (spec.get('lower') is None or v>=spec['lower']) and (spec.get('upper') is None or v<=spec['upper'])
 if passed and spec.get('upper_exclusive'):passed=v<spec['upper']
 if passed and spec.get('lower_exclusive'):passed=v>spec['lower']
 return {'value':v,'passed':passed,'margin':min(ms) if ms else -1.0}
def aggregate(specs,conditions,result):
 rows=result.get('corners',[]);ids=[c['id'] for c in conditions];seen=[c['id'] for c in rows]
 if len(set(seen))!=len(seen) or any(x not in ids for x in seen):raise ValueError('Unexpected/duplicate corner')
 by={c['id']:c for c in rows};per={};cons={}
 for spec in specs:
  key=spec['name'];points={}
  for cid in ids:
   row=by.get(cid,{});values=row.get('values',{});value=values.get(key,values.get(spec.get('metric')))
   # Infrastructure failure must not retain misleading partial scalar passes.
   if not row.get('execution_ok',False):value=None
   points[cid]=single(spec,value)
  missing=[cid for cid,x in points.items() if x['value'] is None]
  worst=missing[0] if missing else min(points,key=lambda cid:points[cid]['margin'])
  w=points[worst];cons[key]={**spec,**w,'conditions':ids,'aggregate':'worst normalized bound margin across every configured corner','worst_condition':worst,'per_corner':points,'passed':all(x['passed'] for x in points.values())}
  per[key]=points
 counts={cid:sum(per[k][cid]['passed'] for k in per) for cid in ids}
 execution_ok=result.get('execution_ok',False) and set(seen)==set(ids) and all(by[x].get('execution_ok',False) for x in ids)
 return cons,{'total_corners':len(ids),'metric_count':len(specs),'per_corner_pass_counts':counts,'all_metrics_pass_corners':sum(x==len(specs) for x in counts.values()),'scalar_passes':sum(counts.values()),'scalar_tests':len(ids)*len(specs),'missing_scalars':sum(v['value'] is None for p in per.values() for v in p.values())},execution_ok
class SizingProblem:
 def __init__(self,task_id,project=None,profile='search_full',mc_samples=None):
  if task_id.endswith('_full'):task_id=task_id[:-5];profile='full_verify'
  self.task_id=task_id;self.profile=profile;self.task=importlib.import_module(TASKS[task_id]).Task(profile=profile);self.cfg=self.task.cfg;self.variables=self.cfg['variables'];self.cfg['conditions']=[dict(x) for x in self.cfg['conditions']]
  for c in self.cfg['constraints']:c['conditions']=[x['id'] for x in self.cfg['conditions']];c['aggregate']='worst'
  details=self.cfg.get('operating_conditions',{})
  self.cfg['operating_conditions_detail']=details
  self.cfg['operating_conditions']={k:v for k,v in details.items() if finite(v)}
  self.cfg['description']+=' Fixed operating-condition details: '+json.dumps(details,sort_keys=True)
  self.project=SimpleNamespace(environment={'execution':{'job_timeout_s':180}});validate(self.variables,self.paper_design())
 def problem(self):return self.cfg
 def paper_design(self):return self.task.seed_design()
 def plan(self,design=None):return SimpleNamespace(dut_text=self.task.plan_text())
 def evaluate(self,design,out_dir,keep_raw=False,request_id=None,defer_recipes=()):
  validate(self.variables,design);out=Path(out_dir)
  if (out/'metrics.json').exists():raise FileExistsError(str(out))
  # Evaluator may require an empty output directory; write root metadata after it returns.
  evaluator=importlib.import_module(TASKS[self.task_id]).Task(profile=self.profile)
  result=evaluator.evaluate(design,out,keep_raw=keep_raw or self.profile=='full_verify',timeout=self.project.environment['execution']['job_timeout_s'])
  cons,counts,ok=aggregate(self.cfg['constraints'],self.cfg['conditions'],result)
  flat={'schema':'analogiq.metrics/1','task_id':self.task_id,'parameters_source':'explicit design','feasible':all(c['passed'] for c in cons.values()) and ok,'feasibility_scope':'configured scalar targets at every corner; bandgap startup is mandatory; DTMOS gain interpretation and remaining topology qualifications are explicit','constraints':cons,'objective':None,'worst_constraint_margin':min(c['margin'] for c in cons.values()),'targets_met':sum(c['passed'] for c in cons.values()),'targets':len(cons),'execution_status':'completed' if ok else 'partial','cost':{'simulator_invocations':result.get('simulator_invocations',0)},'diagnostics':{'corner_summary':counts,'evaluator':{k:v for k,v in result.items() if k!='corners'},'corners':result.get('corners',[])},'operating_points':{},'measurement_profile':self.profile}
  write(out/'adapter_design.json',{'parameters':design,'request_id':request_id});write(out/'metrics.json',flat);return flat
