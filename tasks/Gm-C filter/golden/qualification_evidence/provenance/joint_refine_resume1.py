"""Sequential measured-Jacobian feasibility steps; exact user constraints, fixed connectivity."""
import json,sys,time,os,threading,subprocess,fcntl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import linprog
N=Path(__file__).resolve().parent;R=N.parent
sys.path[:0]=[str(R),str(R/'continuation_20261113')]
import reconstruct as r
from run_policy import apply
apply(r.work)
from feedback_task import FeedbackTask
r.TASK=FeedbackTask();START=time.monotonic();r.DEADLINE=START+1200
ROOT=N/'joint_fit_resume1';ROOT.mkdir(exist_ok=True)
CFG=json.loads((N/'range_only/configuration.json').read_text());KEYS=CFG['keys'];BOUNDS=CFG['bounds'];P=len(KEYS)
LB=np.log([BOUNDS[k][0] for k in KEYS]);UB=np.log([BOUNDS[k][1] for k in KEYS]);LOCK=threading.RLock();COUNT=0;ITER=0;BEST=None;CLOSEST=None

def gvector(e):
 out=[]
 for row in e['corners']:
  for key,(lo,hi,scale) in r.work.LIMITS.items():
   value=row['values'].get(key);valid=row.get('execution_ok') and not row['diagnostics']['errors'] and value is not None and np.isfinite(value)
   if lo is not None:out.append((value-lo)/(.15*scale) if valid else -20.)
   if hi is not None:out.append((hi-value)/(.15*scale) if valid else -20.)
 return np.array(out)

def shape(e):return all(x['diagnostics'].get('filter_response',{}).get('strict_shape_screen') for x in e['corners'])
def quality(e):return (not shape(e),-e['grade']['all_pass'],-e['grade']['scalar_pass'],e['joint_cost'])
def publish(state='running',reason=None):
 data=dict(state=state,reason=reason,pid=os.getpid(),elapsed_s=time.monotonic()-START,completed_designs=COUNT,optimizer_iterations=ITER,golden_verified=False,method='sequential measured-Jacobian linear feasibility with nonlinear validation',best_label=BEST['label'] if BEST else None,best_grade=BEST['grade'] if BEST else None,closest_label=CLOSEST['label'] if CLOSEST else None,closest_cost=CLOSEST['joint_cost'] if CLOSEST else None)
 r.work.dump(ROOT/'status.json',data)
 if BEST:r.work.dump(ROOT/'best_candidate.json',BEST)
 if CLOSEST:r.work.dump(ROOT/'closest_candidate.json',CLOSEST)

def evaluate(x):
 global COUNT,BEST,CLOSEST
 r.guard();d={k:float(np.clip(np.exp(v),*BOUNDS[k])) for k,v in zip(KEYS,x)}
 e=r.run('jointrefine10to20',d,full=True);g=gvector(e);e['joint_cost']=float(np.minimum(g,0)@np.minimum(g,0))+(0. if shape(e) else 1000.)
 with LOCK:
  COUNT+=1
  if BEST is None or quality(e)<quality(BEST):BEST=e
  if CLOSEST is None or e['joint_cost']<CLOSEST['joint_cost']:CLOSEST=e
  with (ROOT/'history.jsonl').open('a') as f:f.write(json.dumps(dict(label=e['label'],cost=e['joint_cost'],grade=e['grade'],design=e['design']))+'\n')
  publish()
  if COUNT%16==0:
   with (ROOT/'archive.log').open('a') as log:subprocess.run([sys.executable,str(R/'archive_completed.py')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
 return e

def solve_step(J,g0,x,radius):
 A=np.vstack([np.hstack([-J,np.zeros_like(J)]),np.hstack([np.eye(P),-np.eye(P)]),np.hstack([-np.eye(P),-np.eye(P)])]);b=np.r_[g0-1e-6,np.zeros(2*P)]
 bounds=[(max(LB[i]-x[i],-radius),min(UB[i]-x[i],radius)) for i in range(P)]+[(0,None)]*P
 return linprog(np.r_[np.zeros(P),np.ones(P)],A_ub=A,b_ub=b,bounds=bounds,method='highs')

def main():
 global ITER
 lock=(ROOT/'run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (ROOT/'history.jsonl').exists():raise RuntimeError('Preserve previous joint run')
 seed=json.loads((R/'trials/joint_feasible_radius_0.05_9e69307afbf1/design.json').read_text());x=np.log([seed[k] for k in KEYS])
 r.work.dump(ROOT/'configuration.json',dict(keys=KEYS,bounds=BOUNDS,initial_design=seed,conditions=r.work.CONDITIONS,limits=r.work.LIMITS,difference_log_step=.002,wall_limit_s=1200,max_iterations=8))
 e=evaluate(x)
 try:
  for iteration in range(8):
   ITER=iteration
   if e['grade']['all_pass']==9 and shape(e):publish('finished','Scalar candidate ready for fresh dense and physical qualification');return
   g0=gvector(e);probes=[];steps=[]
   for j in range(P):
    step=.002 if x[j]+.002<=UB[j] else -.002
    xp=x.copy();xp[j]+=step;assert LB[j]<=xp[j]<=UB[j];probes.append(xp);steps.append(step)
   with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(evaluate,probes))
   if BEST and BEST['grade']['all_pass']==9 and shape(BEST):publish('finished','Scalar candidate ready for fresh dense and physical qualification');return
   J=np.column_stack([(gvector(v)-g0)/step for v,step in zip(results,steps)])
   r.work.dump(ROOT/f'jacobian_{iteration}.json',dict(base=e['label'],keys=KEYS,values=J.tolist(),constraints=g0.tolist(),probes=[z['label'] for z in results]))
   trials=[]
   for radius in [.02,.05,.1,.2]:
    solution=solve_step(J,g0,x,radius)
    if not solution.success:continue
    for fraction in [1.,.5]:
     xn=np.clip(x+fraction*solution.x[:P],LB,UB);v=evaluate(xn);trials.append((v,xn))
     if v['grade']['all_pass']==9 and shape(v):publish('finished','Scalar candidate ready for fresh dense and physical qualification');return
    if min(v['joint_cost'] for v,_ in trials)<e['joint_cost']*.95:break
   with (ROOT/'archive.log').open('a') as log:subprocess.run([sys.executable,str(R/'archive_completed.py')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
   candidates=trials+[(v,xp) for v,xp in zip(results,probes)]
   if not candidates:publish('finished','No linear feasible step within tested trust regions');return
   next_e,next_x=min(candidates,key=lambda a:a[0]['joint_cost'])
   if next_e['joint_cost']>=e['joint_cost']-1e-8:publish('finished','Joint feasibility round stalled; no golden');return
   e,x=next_e,next_x;publish()
  publish('finished','Iteration limit reached; inspect actual results')
 except InterruptedError as ex:publish('stopped',str(ex))
if __name__=='__main__':main()
