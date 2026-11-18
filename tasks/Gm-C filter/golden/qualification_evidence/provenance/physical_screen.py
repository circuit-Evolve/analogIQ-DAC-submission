"""Finite pole/step screening of a frozen candidate, not an unrestricted stability proof."""
import json,re,shutil,time,hashlib,os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import reconstruct as r
from compact import CompactTask
from untied import UntiedTask
from engine import read_wave

PAIRS=[('A','DUT.AP','DUT.AM'),('B','DUT.BP','DUT.BM'),('D','DUT.DP','DUT.DM'),('OUT','VOP','VOM')]
NODES={'VIP','VIM'}|{n for _,p,m in PAIRS for n in (p,m)}
BIAS_NODES={f'DUT.OTA{i}.{n}' for i in range(1,5) for n in ('N','FB','BP','BN')}
NODES |= BIAS_NODES
DM_STEP_V=float(os.environ.get('GMC_SCREEN_DM_STEP_V','0.001'))
if not 1e-5<=DM_STEP_V<=.001:raise ValueError('Unsupported small-signal step amplitude')

def parse_poles(log):
 if log.count('Poles (Hz)')!=1:raise ValueError('Missing or duplicate pole table')
 sec=log.split('Poles (Hz)')[1].split('Accumulated DC')[0]
 lines=[line for line in sec.splitlines() if re.match(r'^\s*\d+\s',line)]
 poles=[];indices=[]
 for line in lines:
  m=re.fullmatch(r'\s*(\d+)\s+([-+0-9.eE]+)\s+(\+/-\s+)?([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*',line)
  if not m:raise ValueError('Unparsed pole row: '+line)
  indices.append(int(m[1]));a,b=float(m[2]),float(m[4])
  if not np.isfinite(a) or not np.isfinite(b):raise ValueError('Nonfinite pole')
  poles.append([a,b])
  if m[3]:poles.append([a,-b])
 if not indices or indices!=list(range(1,len(indices)+1)):raise ValueError('Incomplete pole row sequence')
 return poles

def wave_check(t,signals):
 if len(t)<99000 or not np.all(np.isfinite(t)) or np.any(np.diff(t)<=0):raise ValueError('Invalid time grid')
 if t[0]>1e-15 or t[-1]<499.99e-9 or np.max(np.diff(t))>5.01e-12:raise ValueError('Incomplete transient or insufficient time resolution')
 if set(signals)!=NODES or any(len(v)!=len(t) or not np.all(np.isfinite(v)) for v in signals.values()):raise ValueError('Missing/nonfinite waveforms')

def screen(design,corner,label):
 task=UntiedTask() if 'M19_w' in design else CompactTask()
 out=r.RAW/label/corner['id'];dest=r.ROOT/label/corner['id']
 if out.exists():raise RuntimeError('Screen output already exists; use a fresh label')
 base=task.corner_decks(design,corner)['FILTER_AC_NOISE']
 base=re.sub(r'(?m)^(ac ac|noise \(VOP VOM\)).*\n','',base)
 base+='save '+' '.join(sorted(BIAS_NODES))+'\n'
 decks={'PZ':base+'poles pz method=arnoldi numpoles=80\n'}
 cm=corner['input_common_mode_V']
 for mode in ('DM','CM'):
  deck=base
  for name,node,sign in [('VINP','VIP',1),('VINM','VIM',-1 if mode=='DM' else 1)]:
   delta=sign*(DM_STEP_V/2 if mode=='DM' else .0001)
   mag=sign*(.5 if mode=='DM' else 1.)
   deck=re.sub(r'(?m)^'+name+r' .*$',f'{name} ({node} 0) vsource dc={cm:.12g} mag={mag} type=pulse val0={cm:.12g} val1={cm+delta:.12g} delay=100n rise=10p fall=10p width=1u period=2u',deck)
  deck+='ac ac start=1 stop=1.01 lin=2\nstep tran stop=500n maxstep=5p strobeperiod=5p errpreset=conservative\n'
  decks[mode]=deck
 jobs=[]
 # Sequential jobs bound memory and disk while the sizing workers are active.
 for item in decks.items():jobs.append(task._simulate(item,out,corner,180,time.monotonic()+190))
 result=dict(corner=corner,design_sha256=hashlib.sha256(json.dumps(design,sort_keys=True).encode()).hexdigest(),jobs={j:s for j,p,s in jobs},paper_exact=False,errors={},golden_verified=False,requested_DM_step_V=DM_STEP_V)
 for job,path,status in jobs:
  if status['returncode']!=0:
   result['errors'][job]='Simulator failed';continue
  try:
   if job=='PZ':
    log=(path/'spectre.log').read_text();poles=parse_poles(log)
    result['poles_Hz']=poles;result['all_reported_poles_LHP']=all(a<0 for a,b in poles)
    result['four_dominant_real_poles']=sum(a<0 and abs(b)<1 and abs(a)<200e6 for a,b in poles)==4
    result['pole_caveat']='Arnoldi finite pole set; installed BSIM3 PZ analysis approximates frequency-dependent terms at 1 Hz. Not a proof of unrestricted stability.'
   else:
    files=list((path/'raw').glob('*.tran'))
    if len(files)!=1:raise ValueError('Missing/ambiguous transient')
    t,v=read_wave(files[0],NODES);wave_check(t,v)
    f,a=read_wave(path/'raw/ac.ac',NODES)
    if not len(f) or not np.isclose(f[0],1) or any(not np.all(np.isfinite(x)) for x in a.values()):raise ValueError('Invalid AC reference')
    pre=(t>=50e-9)&(t<=90e-9);post=t>=450e-9;tail=t>=400e-9
    incoming=v['VIP']-v['VIM'] if job=='DM' else (v['VIP']+v['VIM'])/2
    vin=float(np.median(incoming[post])-np.median(incoming[pre]));expected=DM_STEP_V if job=='DM' else .0001
    if not np.isclose(vin,expected,rtol=1e-7,atol=1e-12):raise ValueError('Actual stimulus differs from requested step')
    channels={};columns=[t,incoming];names=['time_s','input_V']
    for stage,p,m in PAIRS:
     for kind,y,ac in [('DM',v[p]-v[m],a[p][0]-a[m][0]),('CM',(v[p]+v[m])/2,(a[p][0]+a[m][0])/2)]:
      name=stage+'_'+kind;before=float(np.median(y[pre]));after=float(np.median(y[post]));delta=after-before
      tail_pp=float(np.ptp(y[tail]));predicted=float(ac.real*vin)
      settle=tail_pp<=max(1e-8,.001*abs(delta))
      agreement=abs(delta-predicted)<=max(1e-7,.03*abs(predicted))
      channels[name]=dict(initial_V=before,final_V=after,delta_V=delta,ac_predicted_delta_V=predicted,tail_pp_V=tail_pp,settled=bool(settle),small_signal_agreement=bool(agreement))
      columns.append(y);names.append(name+'_V')
    for node in sorted(BIAS_NODES):
     y=v[node];before=float(np.median(y[pre]));after=float(np.median(y[post]));delta=after-before
     tail_pp=float(np.ptp(y[tail]));predicted=float(a[node][0].real*vin)
     channels[node]=dict(initial_V=before,final_V=after,delta_V=delta,ac_predicted_delta_V=predicted,tail_pp_V=tail_pp,settled=bool(tail_pp<=max(1e-8,.001*abs(delta))),small_signal_agreement=bool(abs(delta-predicted)<=max(1e-7,.03*abs(predicted))))
     columns.append(y);names.append(node+'_V')
    rails=all(np.min(v[n])>=-.05 and np.max(v[n])<=corner['supply_V']+.05 for n in NODES)
    passed=all(x['settled'] and x['small_signal_agreement'] for x in channels.values()) and rails
    result[job]=dict(actual_input_step_V=vin,channels=channels,within_rails=bool(rails),screen_pass=bool(passed),samples=len(t),max_step_s=float(np.max(np.diff(t))))
    # Full-resolution diagnostics above; export decimated waveform for compact replay evidence.
    np.savetxt(out/(job+'_step_decimated.csv'),np.column_stack(columns)[::100],delimiter=',',header=','.join(names),comments='')
    np.savez_compressed(out/(job+'_full_resolution.npz'),time_s=t,ac_frequency_Hz=f,**v,**{'AC__'+k:x for k,x in a.items()})
  except Exception as ex:result['errors'][job]=str(ex)
 result['physical_screen_pass']=bool(not result['errors'] and result.get('all_reported_poles_LHP') and result.get('four_dominant_real_poles') and result.get('DM',{}).get('screen_pass') and result.get('CM',{}).get('screen_pass'))
 r.work.dump(out/'screen.json',result)
 task._retain_or_prune(out,False);shutil.copytree(out,dest,dirs_exist_ok=True)
 return result

if __name__=='__main__':
 import sys
 candidate=json.loads(open(sys.argv[1]).read());design=candidate.get('design',candidate);label=sys.argv[2]
 r.work.dump(r.ROOT/label/'design.json',design)
 with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda c:screen(design,c,label),r.work.CONDITIONS))
 r.work.dump(r.ROOT/label/'summary.json',dict(corners=rows,physical_screen_pass=sum(x['physical_screen_pass'] for x in rows),total=len(rows),golden_verified=False))
