import json,sys
from pathlib import Path
N=Path(__file__).resolve().parent;R=N.parent
sys.path[:0]=[str(R),str(R/'continuation_20261113')]
import reconstruct as r
from run_policy import apply
apply(r.work)
from feedback_task import FeedbackTask
r.TASK=FeedbackTask();base=json.loads((R/'trials/crosslength_n2_p1_0c773ba1562f/design.json').read_text());rows=[]
for ki in [1.3,1.6,2.]:
 for kc in [.95,1.05,1.15,1.25]:
  d=dict(base)
  for k in ['input_n_w','input_p_w']:d[k]*=ki
  d['cross_n_w']*=kc
  for k in ['cap_b_F','cap_d_F']:d[k]*=.98
  e=r.run('longcross_input_%g_cross_%g'%(ki,kc),d,full=True);f=[x['values'].get('Filter_cutoff_Hz') for x in e['corners']];valid=all(v and v>0 for v in f)
  row=dict(label=e['label'],input_scale=ki,cross_scale=kc,grade=e['grade'],cutoff_range=[min(f),max(f)] if valid else None,spread=max(f)/min(f) if valid else None,shapes=sum(x['diagnostics'].get('filter_response',{}).get('strict_shape_screen',False) for x in e['corners']))
  rows.append(row);r.work.dump(N/'cross_input_probe_results.json',rows);print('LONGCROSS',ki,kc,e['grade']['all_pass'],e['grade']['scalar_pass'],row['spread'],flush=True)
  if e['grade']['all_pass']==9 and row['shapes']==9:raise SystemExit
