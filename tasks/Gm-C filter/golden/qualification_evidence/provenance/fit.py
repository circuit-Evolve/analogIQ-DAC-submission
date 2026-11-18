"""Fit all nine conditions simultaneously; fixed topology and target definitions."""
import sys,os,json,time,math,threading,hashlib,traceback,fcntl,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import least_squares
sys.path[:0]=[str(Path(__file__).resolve().parent.parent),str(Path(__file__).resolve().parent.parent/'continuation_20261113')]
import reconstruct as r
from run_policy import apply
POLICY=apply(r.work)
from feedback_task import FeedbackTask
COMPACT=True
r.TASK=FeedbackTask()
START=time.monotonic();r.DEADLINE=START+1200
ROOT=r.ROOT/'cutoff_10_20MHz_20261113/fit';ROOT.mkdir(exist_ok=True)
VARIABLES=r.TASK.variables+r.TASK.extra_variables+r.TASK.feedback_variables
KEYS=[v['name'] for v in VARIABLES]
BOUNDS={v['name']:(v['lower'],v['upper']) for v in VARIABLES}
BASE=json.loads((r.ROOT/'cutoff_10_20MHz_20261113/starting_design.json').read_text())
LOCK=threading.RLock();DESIGN_LOCKS={};COUNT=0;BEST=None;ITERATION=0;CACHE={}

def vector_residual(e):
 out=[]
 for row in e['corners']:
  valid=row.get('execution_ok',False) and not row.get('diagnostics',{}).get('errors',{})
  vals=row['values']
  for m,(lo,hi,scale) in r.work.LIMITS.items():
   # Interior search margin only; final grading keeps exact user limits.
   margin={'OTA_differential_gain_dB':.15,'OTA_unity_gain_frequency_Hz':25e6,'OTA_phase_margin_deg':.1,'OTA_common_mode_gain_dB':.1,'Filter_cutoff_Hz':50e3,'Filter_input_noise_nV_sqrtHz':.25}[m]
   if lo is not None:lo+=margin
   if hi is not None:hi-=margin
   v=vals.get(m)
   if not valid or v is None or not math.isfinite(v):out.append(20.);continue
   out.append(max(0.,(lo-v)/(.15*scale) if lo is not None else 0.,(v-hi)/(.15*scale) if hi is not None else 0.))
  for m,mid in [('OTA_unity_gain_frequency_Hz',1e10),('Filter_cutoff_Hz',15e6)]:
   v=vals.get(m)
   if r.work.LIMITS[m][1] is not None:out.append(.03*(v-mid)/(.15*mid) if valid and v is not None else 20.)
  out.append(0. if row.get('diagnostics',{}).get('filter_response',{}).get('strict_shape_screen') else 20.)
 return np.array(out)

def publish(state='running',reason=None):
 data=dict(state=state,reason=reason,pid=os.getpid(),elapsed_s=time.monotonic()-START,completed_designs=COUNT,
  optimizer_iterations=ITERATION,method='bounded simultaneous nine-condition least-squares sizing',
  golden_verified=False,topology='144MOS reconstruction; original OTA connectivity; six CM/bias devices and existing filter-feedback n/p geometry independently sized',
  best_label=BEST['label'] if BEST else None,best_grade=BEST['grade'] if BEST else None,
  best_sum_square_residual=BEST['fit_cost'] if BEST else None)
 r.work.dump(ROOT/'status.json',data)
 if BEST:
  r.work.dump(ROOT/'best_candidate.json',BEST);r.work.dump(ROOT/'best_design.json',BEST['design'])

def fitness_key(e):
 shape=all(row['diagnostics'].get('filter_response',{}).get('strict_shape_screen') for row in e['corners'])
 return (not shape,-e['grade']['all_pass'],-e['grade']['scalar_pass'],e['fit_cost'])

def objective(x):
 global COUNT,BEST
 r.guard();d={k:float(np.clip(np.exp(z),*BOUNDS[k])) for k,z in zip(KEYS,x)}
 key=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
 with LOCK:dl=DESIGN_LOCKS.setdefault(key,threading.Lock())
 with dl:
  with LOCK:
   if key in CACHE:return CACHE[key].copy()
   if COUNT>=1000:raise InterruptedError('1000-design evaluation limit')
  e=r.run('cutoff10to20_fit',d,full=True);v=vector_residual(e);e['fit_cost']=float(v@v)
  with LOCK:
   COUNT+=1;CACHE[key]=v
   if BEST is None or fitness_key(e)<fitness_key(BEST):BEST=e
   with (ROOT/'history.jsonl').open('a') as f:f.write(json.dumps(dict(label=e['label'],cost=e['fit_cost'],grade=e['grade'],design=d))+'\n')
   publish()
   if COUNT%40==0:
    with (ROOT/'archive.log').open('a') as log:subprocess.run([sys.executable,str(r.ROOT/'archive_completed.py')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
   print('FIT',COUNT,'cost',round(e['fit_cost'],5),'pass',e['grade']['scalar_pass'],'full',e['grade']['all_pass'],flush=True)
  return v

def callback(result):
 global ITERATION
 with LOCK:
  ITERATION+=1;publish()
  if BEST and BEST['grade']['all_pass']==9 and all(row['diagnostics']['filter_response']['strict_shape_screen'] for row in BEST['corners']):raise StopIteration

def main():
 global BEST
 f=(ROOT/'run.lock').open('w');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (ROOT/'history.jsonl').exists():raise RuntimeError('Preserve existing fitting run; choose explicit new run root')
 r.work.dump(ROOT/'configuration.json',dict(keys=KEYS,bounds=BOUNDS,initial_design=BASE,conditions=r.work.CONDITIONS,limits=r.work.LIMITS,
  wall_limit_s=1200,max_nfev=35,max_designs=1000,workers=4,measurement_definitions_unchanged=True))
 publish()
 x0=np.log([BASE[k] for k in KEYS]);lb=np.log([BOUNDS[k][0] for k in KEYS]);ub=np.log([BOUNDS[k][1] for k in KEYS])
 try:
  with ThreadPoolExecutor(max_workers=4) as pool:
   result=least_squares(objective,x0,bounds=(lb,ub),jac='2-point',diff_step=.0002/np.maximum(abs(x0),.05),
    x_scale=.05,ftol=1e-7,xtol=1e-9,gtol=1e-5,max_nfev=35,workers=pool.map,callback=callback,verbose=1)
  r.work.dump(ROOT/'optimizer.json',dict(message=str(result.message),status=int(result.status),cost=float(result.cost),nfev=int(result.nfev),njev=int(result.njev or 0),design={k:float(np.exp(v)) for k,v in zip(KEYS,result.x)}))
  publish('finished','Scalar match requires fresh physical qualification' if BEST and BEST['grade']['all_pass']==9 else 'Optimizer round finished; review actual residuals')
 except InterruptedError as ex:publish('stopped',str(ex))
 except Exception as ex:
  r.work.dump(ROOT/'error.json',dict(error=repr(ex),traceback=traceback.format_exc()));publish('error',str(ex));raise

if __name__=='__main__':main()
