import json,sys
from pathlib import Path
N=Path(__file__).resolve().parent;R=N.parent
sys.path[:0]=[str(R),str(R/'continuation_20261113')]
import reconstruct as r
from run_policy import apply
apply(r.work)
from feedback_task import FeedbackTask
r.TASK=FeedbackTask();base=json.loads((N/'elastic_fit/accepted_candidate.json').read_text())['design'];rows=[]
for nf,pf in [(2,1),(3,1),(4,1),(1,2),(2,2)]:
 d=dict(base)
 for typ,factor in [('n',nf),('p',pf)]:
  for par in ['w','l']:d['cross_'+typ+'_'+par]*=factor
 e=r.run('crosslength_n%d_p%d'%(nf,pf),d,full=True);fs=[x['values'].get('Filter_cutoff_Hz') for x in e['corners']];valid=all(f and f>0 for f in fs)
 row=dict(label=e['label'],n=nf,p=pf,grade=e['grade'],cutoff_range=[min(fs),max(fs)] if valid else None,spread=max(fs)/min(fs) if valid else None,shapes=sum(x['diagnostics'].get('filter_response',{}).get('strict_shape_screen',False) for x in e['corners']))
 rows.append(row);r.work.dump(N/'cross_length_probe_results.json',rows);print('CROSS',json.dumps(row),flush=True)
