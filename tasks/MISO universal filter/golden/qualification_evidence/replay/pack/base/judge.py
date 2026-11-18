"""Frozen run-local judges; shared curator LEDRO implementation remains unmodified."""
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import importlib,json,math,numbers,shutil
from engine import execute
P=Path(__file__).resolve().parent
TASKS={'gm_c':'gm_c_task','bandgap':'bandgap_task','dtmos':'dtmos_task','miso':'miso_task'}
def validate_design(variables,design):
 if set(design)!={v['name'] for v in variables}:raise ValueError('Design must specify all sizing variables exactly')
 for v in variables:
  x=design[v['name']]
  if isinstance(x,bool) or not isinstance(x,numbers.Real) or not math.isfinite(x) or not v['lower']<=x<=v['upper']:raise ValueError('Invalid or out-of-bounds sizing: '+v['name'])
def score_constraints(specs,values):
 out={}
 for s in specs:
  x=values.get(s['name'])
  x=float(x) if isinstance(x,numbers.Real) and not isinstance(x,bool) and math.isfinite(x) else None
  passed=x is not None and (s.get('lower') is None or x>=s['lower']) and (s.get('upper') is None or x<=s['upper'])
  if passed and s.get('upper_exclusive'):passed=x<s['upper']
  if passed and s.get('lower_exclusive'):passed=x>s['lower']
  margins=[];scale=abs(s['paper_value']) or 1.
  if x is not None:
   if s.get('lower') is not None:margins.append((x-s['lower'])/scale)
   if s.get('upper') is not None:margins.append((s['upper']-x)/scale)
  out[s['name']]={**s,'value':x,'passed':passed,'margin':min(margins) if margins else -1.}
 return out

def json_default(x):
 if isinstance(x,numbers.Real):return float(x) if math.isfinite(x) else None
 if isinstance(x,Path):return str(x)
 if hasattr(x,'tolist'):return x.tolist()
 raise TypeError(type(x).__name__)
def write_json(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,default=json_default,allow_nan=False));tmp.replace(path)

class SizingProblem:
 def __init__(self,task_id,project=None,profile='search_full',mc_samples=None):
  if task_id.endswith('_full'):task_id=task_id[:-5];profile='full_verify'
  if task_id not in TASKS:raise ValueError('Unknown run-local task '+task_id)
  self.task_id=task_id;self.profile=profile;self.task=importlib.import_module(TASKS[task_id]).Task(profile=profile);self.cfg=self.task.cfg;self.variables=self.cfg['variables']
  self.project=SimpleNamespace(environment={'execution':{'job_timeout_s':180}})
  validate_design(self.variables,self.paper_design())
 def problem(self):return self.cfg
 def paper_design(self):return self.task.paper_design()
 def plan(self,design=None):return SimpleNamespace(dut_text=self.task.plan_text())
 def evaluate(self,design,out_dir,keep_raw=False,request_id=None,defer_recipes=()):
  validate_design(self.variables,design);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
  if (out/'metrics.json').exists():raise FileExistsError('Refusing to overwrite completed evaluation: '+str(out))
  write_json(out/'design.json',{'parameters':design,'request_id':request_id});decks=self.task.decks(design)
  keep_raw=keep_raw or self.profile=='full_verify'
  def one(item):
   name,deck=item;path=out/name;error=None
   try:rc=execute(deck,path,timeout=float(self.project.environment['execution']['job_timeout_s']))
   except Exception as e:rc=1;error=type(e).__name__+': '+str(e)
   return dict(name=name,path=str(path),returncode=rc,error=error)
  with ThreadPoolExecutor(max_workers=2) as pool:jobs=list(pool.map(one,decks.items()))
  paths={j['name']:Path(j['path']) for j in jobs if j['returncode']==0};values={};diagnostics={};extract_error=None
  try:values,diagnostics=self.task.extract(paths)
  except Exception as e:extract_error=type(e).__name__+': '+str(e)
  cons=score_constraints(self.cfg['constraints'],values);met=sum(c['passed'] for c in cons.values());execution_ok=all(j['returncode']==0 for j in jobs) and extract_error is None
  diagnostics={**diagnostics,'jobs':jobs,'extraction_error':extract_error,'measurement_profile':self.profile}
  flat=dict(schema='analogiq.metrics/1',task_id=self.task_id,parameters_source='explicit design',feasible=met==len(cons) and execution_ok,constraints=cons,objective=None,worst_constraint_margin=min(c['margin'] for c in cons.values()),targets_met=met,targets=len(cons),execution_status='completed' if execution_ok else 'partial',cost={'simulator_invocations':len(jobs)},diagnostics=diagnostics,operating_points={},measurement_profile=self.profile)
  write_json(out/'metrics.json',flat)
  if not keep_raw:
   for j in jobs:shutil.rmtree(Path(j['path'])/'raw',ignore_errors=True)
  return flat
