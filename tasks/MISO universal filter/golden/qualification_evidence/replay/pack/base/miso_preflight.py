from pathlib import Path
import concurrent.futures,json,sys,hashlib,time,re
import numpy as np
from miso_task import Task,TEMPLATES
from engine import execute,num

R=Path(__file__).resolve().parent.parent; O=R/'preflight/miso';O.mkdir(parents=True,exist_ok=True)
t=Task();seed=t.paper_design();decks=t.decks(seed)
assert len(t.variables)==26 and len(t.cfg['constraints'])==17 and len(decks)==12
assert all(decks[j]==(TEMPLATES/(j+'.scs')).read_text() for j in decks)
assert len(Task('full').decks(seed))==20
for bad in [{},dict(seed,extra=1),dict(seed,C1=float('nan')),dict(seed,C1=0),dict(seed,C1=True)]:
 try:t.decks(bad)
 except ValueError:pass
 else:raise AssertionError('invalid sizing accepted')
mutation_checks=[]
for v in t.variables:
 d=dict(seed);d[v['name']]=v['initial']+(v['upper']-v['initial'])*.1;changed=t.decks(d);b=v['binding'];count=0
 for job,s in changed.items():
  if b['cell']=='__top__':body=s
  else:
   m=re.search(r'^subckt '+b['cell']+r' .*?\n(.*?)^ends '+b['cell'],s,re.M|re.S)
   if not m:assert s==decks[job];continue
   body=m[1]
  for dev in b['instances']:
   line=re.search(r'^\s*'+dev+r' \([^\n]+\) [^\n]+',body,re.M)[0];params=dict(re.findall(r'(\w+)=(\S+)',line));assert np.isclose(num(params[b['parameter']]),d[v['name']],rtol=1e-10,atol=0);count+=1
  # All analysis lines, input stimuli, supplies, functional loads unchanged.
  def fixed(s):
   return [line for line in s.splitlines() if (line.startswith(('ac ','ac_fine ','noise ','tran ','range ','simulatorOptions ','RXLOAD ')) or ('_SRC (' in line and not line.startswith(('VBIAS_SRC ','VCTRL_SRC '))))]
  assert fixed(s)==fixed(decks[job])
 assert count>0
 mutation_checks.append({'variable':v['name'],'verified_instance_bindings':count})
# Missing paths must produce missing values, never invented successful outputs.
missing,md=t.extract({});assert all(v is None for v in missing.values())
(O/'binding_checks.json').write_text(json.dumps({'paper_seed_byte_identical':True,'invalid_designs_rejected':5,'missing_values_fail':True,'mutation_checks':mutation_checks},indent=2))
start=time.monotonic()
def run(item):
 job,deck=item;p=O/'seed'/job;return job,p,execute(deck,p,timeout=180)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,decks.items()))
paths={job:p for job,p,rc in results if rc==0};assert len(paths)==len(decks),results
values,diag=t.extract(paths)
(O/'seed_values.json').write_text(json.dumps(values,indent=2));(O/'seed_diagnostics.json').write_text(json.dumps(diag,indent=2))
saved={m['name']:m['result'] for m in json.loads((TEMPLATES/'metrics.json').read_text())};compare=[]
for name,val in values.items():
 assert val is not None,(name,diag)
 error=(val-saved[name])/saved[name];compare.append({'metric':name,'saved':saved[name],'fresh':val,'relative_error':error})
 assert abs(error)<2e-6,(name,val,saved[name],error)
report={'passed':True,'runtime_seconds':time.monotonic()-start,'spectre_jobs':len(decks),'max_parallel_spectre':2,'scalar_count':len(values),'comparisons':compare}
(O/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
