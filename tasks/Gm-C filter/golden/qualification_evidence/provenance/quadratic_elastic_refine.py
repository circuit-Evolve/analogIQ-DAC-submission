"""Small elastic feasibility steps with measured model-agreement trust regions."""
import json,sys,time,fcntl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import linprog, minimize, LinearConstraint
import joint_refine_resume2 as b
N=Path(__file__).resolve().parent
b.ROOT=N/'quadratic_elastic_fit';b.ROOT.mkdir(exist_ok=True);b.START=time.monotonic();b.r.DEADLINE=b.START+1200
MARGIN=.001

def smooth_gvector(e):
 out=[]
 for row in e['corners']:
  for key,(lo,hi,scale) in b.r.work.LIMITS.items():
   value=row['values'].get(key);valid=row.get('execution_ok') and not row['diagnostics']['errors'] and value is not None and np.isfinite(value);den=.15*scale
   if lo is not None:
    out.append((1-10**((lo-value)/20))/(np.log(10)/20*den) if valid and key=='OTA_differential_gain_dB' else (value-lo)/den if valid else -20.)
   if hi is not None:
    out.append((1-10**((value-hi)/20))/(np.log(10)/20*den) if valid and key=='OTA_common_mode_gain_dB' else (hi-value)/den if valid else -20.)
 return np.array(out)
b.gvector=smooth_gvector
_original_publish=b.publish
def publish(state='running',reason=None):
 _original_publish(state,reason)
 data=json.loads((b.ROOT/'status.json').read_text());data['method']='convex elastic QP with smooth equivalent gain constraints and nonlinear trust-region validation'
 accepted=b.ROOT/'accepted_candidate.json'
 if accepted.exists():
  a=json.loads(accepted.read_text());data.update(accepted_label=a['label'],accepted_grade=a['grade'],accepted_elastic_merit=merit(a))
 data['closest_cost_definition']='Squared transformed violations, including rejected probes; accepted_elastic_merit is the optimization progress measure.'
 if b.BEST and done(b.BEST):data['candidate_for_verification']=b.BEST['label']
 b.r.work.dump(b.ROOT/'status.json',data)
b.publish=publish

def merit(e):return float(np.maximum(MARGIN-b.gvector(e),0).sum())+(0. if b.shape(e) else 1000.)
def done(e):return e['grade']['all_pass']==9 and b.shape(e)
def step(J,g,x,radius):
 p=b.P;m=len(g);z=np.zeros((p,m))
 A=np.vstack([np.hstack([-J,np.zeros((m,p)),-np.eye(m)]),np.hstack([np.eye(p),-np.eye(p),z]),np.hstack([-np.eye(p),-np.eye(p),z])])
 rhs=np.r_[g-MARGIN,np.zeros(2*p)]
 bounds=[(max(b.LB[i]-x[i],-radius),min(b.UB[i]-x[i],radius)) for i in range(p)]+[(0,None)]*(p+m)
 linear=linprog(np.r_[np.zeros(p),np.full(p,1e-6),np.ones(m)],A_ub=A,b_ub=rhs,bounds=bounds,method='highs')
 if not linear.success:return linear
 # Convex elastic QP: L1 feasibility slacks plus distributed L2 step regularization.
 aq=np.hstack([-J,-np.eye(m)]);bq=g-MARGIN
 bds=bounds[:p]+[(0,None)]*m;z0=np.r_[linear.x[:p],linear.x[2*p:]]
 def fun(z):return float(z[p:].sum()+5.*(z[:p]@z[:p]))
 def jac(z):return np.r_[10.*z[:p],np.ones(m)]
 sol=minimize(fun,z0,jac=jac,bounds=bds,constraints=[LinearConstraint(aq,-np.inf,bq)],method='SLSQP',options={'ftol':1e-11,'maxiter':250})
 if not sol.success:raise RuntimeError('Convex elastic QP failed: '+sol.message)
 if np.max(aq@sol.x-bq)>1e-7:raise RuntimeError('QP residual exceeds numerical guard')
 return sol

def main():
 lock=(b.ROOT/'run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (b.ROOT/'history.jsonl').exists():raise RuntimeError('Preserve previous elastic run')
 seed=json.loads((N/'smooth_elastic_fit/accepted_candidate.json').read_text())['design'];x=np.log([seed[k] for k in b.KEYS]);radius=.02;accepted=0
 b.r.work.dump(b.ROOT/'configuration.json',dict(method='elastic convex QP, L1 slacks plus 5*sum(log-step squared); same exact acceptance limits',keys=b.KEYS,bounds=b.BOUNDS,initial_design=seed,conditions=b.r.work.CONDITIONS,limits=b.r.work.LIMITS,normalized_search_margin=MARGIN,initial_log_radius=radius,max_log_radius=.08,wall_limit_s=1200,max_outer_iterations=8))
 e=b.evaluate(x);e['elastic_merit']=merit(e);b.r.work.dump(b.ROOT/'accepted_candidate.json',e);b.publish()
 try:
  for outer in range(8):
   b.ITER=outer
   if done(e) or (b.BEST and done(b.BEST)):b.publish('finished','Scalar candidate ready for independent qualification');return
   g=b.gvector(e);dx_probe=min(.002,max(.0002,radius/5));probes=[];steps=[]
   for j in range(b.P):
    h=dx_probe if x[j]+dx_probe<=b.UB[j] else -dx_probe
    xp=x.copy();xp[j]+=h;assert b.LB[j]<=xp[j]<=b.UB[j];probes.append(xp);steps.append(h)
   with ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(b.evaluate,probes))
   if b.BEST and done(b.BEST):b.publish('finished','Scalar candidate ready for independent qualification');return
   J=np.column_stack([(b.gvector(v)-g)/h for v,h in zip(values,steps)])
   b.r.work.dump(b.ROOT/f'jacobian_{outer}.json',dict(base=e['label'],keys=b.KEYS,values=J.tolist(),constraints=g.tolist(),probes=[v['label'] for v in values]))
   accepted_this=0
   for attempt in range(8):
    b.r.guard();sol=step(J,g,x,radius)
    if not sol.success:raise RuntimeError('Elastic LP failed: '+sol.message)
    dx=sol.x[:b.P];predicted=float(np.maximum(MARGIN-(g+J@dx),0).sum());before=merit(e);pred_reduction=before-predicted
    if max(abs(dx))<1e-8 or pred_reduction<1e-8:break
    xn=np.clip(x+dx,b.LB,b.UB);v=b.evaluate(xn);actual=merit(v);ratio=(before-actual)/pred_reduction
    event=dict(outer=outer,attempt=attempt,radius=radius,base=e['label'],candidate=v['label'],predicted_merit=predicted,before_merit=before,actual_merit=actual,agreement_ratio=ratio,accepted=bool(ratio>.1 and actual<before),grade=v['grade'])
    with (b.ROOT/'steps.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
    if done(v):
     v['elastic_merit']=actual;b.r.work.dump(b.ROOT/'accepted_candidate.json',v);b.publish('finished','Scalar candidate ready for independent qualification');return
    if ratio>.1 and actual<before:
     gn=b.gvector(v);J=J+np.outer(gn-g-J@dx,dx)/float(dx@dx);e,x,g=v,xn,gn;accepted+=1;accepted_this+=1
     e['elastic_merit']=actual;b.r.work.dump(b.ROOT/'accepted_candidate.json',e)
     if ratio>.75 and max(abs(dx))>.8*radius:radius=min(.08,radius*1.5)
     elif ratio<.25:radius=max(.0005,radius*.5)
    else:radius=max(.0005,radius*.5)
    b.publish()
    if accepted_this>=3:break
   if accepted_this==0 and radius<=.0005:
    b.publish('finished','Elastic refinement reached trust-region floor; no all-corner golden');return
  b.publish('finished','Elastic iteration budget completed; inspect actual results')
 except InterruptedError as ex:b.publish('stopped',str(ex))
 except Exception as ex:b.publish('error',repr(ex));raise
if __name__=='__main__':main()
