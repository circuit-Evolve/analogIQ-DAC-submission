"""Experimental physical four-state OTA-C reconstruction; NOT paper-exact Fig.3."""
from pathlib import Path
import sys,json,re,time,math,shutil,hashlib,concurrent.futures
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import work
from gm_c_corners import Task as OldTask,read_wave
from engine import dc
RAW=Path('<WORK>/four_papers_20261109/gmc_individual_15pct_20261112/reconstruction_20261113')
RAW.mkdir(parents=True,exist_ok=True)
DEADLINE=None

def guard():
 if DEADLINE is not None and time.monotonic()>=DEADLINE:raise InterruptedError('Search deadline reached')
 if (ROOT/'STOP').exists():raise InterruptedError((ROOT/'STOP').read_text())
 if shutil.disk_usage(ROOT).free<1.5e9 or shutil.disk_usage(RAW).free<3e9:raise InterruptedError('Free-space floor reached')

class Task(OldTask):
 def corner_decks(self,design,corner):
  d=dict(design);ratio=d.pop('damping_ratio',1.)
  if not .1<=ratio<=4:raise ValueError('damping_ratio outside bounds')
  decks=super().corner_decks(d,corner)
  lines=['// Experimental reconstruction: four distinct differential capacitor states.',
   '// Same32MOS OTA core; four physical diode feedback MOS per stage; no summing resistors.',
   'subckt filter_four_state_candidate VIP VIM VOP VOM VT VREF VDD GND']
  stages=[('VIP','VIM','AP','AM'),('AP','AM','BP','BM'),('BP','BM','DP','DM'),('DP','DM','VOP','VOM')]
  for i,(ip,im,op,om) in enumerate(stages,1):
   lines.append(f'OTA{i} ({ip} {im} {op} {om} VT VREF VDD GND) ota_fig2_interpreted')
   cap=d['cap_b_F'] if i<=2 else d['cap_d_F']
   # Differential capacitor; all four values are design assumptions absent from target paper.
   lines.append(f'C{i} ({op} {om}) capacitor c={cap:.12g}')
   for side,node in [('P',op),('M',om)]:
    for typ,rail in [('n','GND'),('p','VDD')]:
     w=max(d['input_'+typ+'_w']*ratio,1.2e-7 if typ=='n' else 2.36e-7);l=d['input_'+typ+'_l']
     lines.append(f'FD{i}{side}{typ} ({node} {node} {rail} {rail}) gpdk090_{typ}mos1v w={w:.12g} l={l:.12g} m=1 as={w*.28e-6:.12g} ad={w*.28e-6:.12g} ps={2*w+.56e-6:.12g} pd={2*w+.56e-6:.12g}')
  lines.append('ends filter_four_state_candidate')
  for job,deck in decks.items():
   # Remove both unused experimental old filter definitions to keep the netlist unambiguous.
   deck=re.sub(r'(?ms)^subckt ota_side_sum_assumption .*?^ends filter_fig3_reconstruction\s*','\n'.join(lines)+'\n',deck)
   if job=='FILTER_AC_NOISE':
    deck=deck.replace(') filter_fig3_reconstruction',') filter_four_state_candidate')
   decks[job]=deck
  return decks

 def _simulate(self,item,out,corner,timeout,deadline=None):
  guard()
  if DEADLINE is not None:deadline=min(deadline,DEADLINE) if deadline is not None else DEADLINE
  return super()._simulate(item,out,corner,timeout,deadline)

 def _shape(self,path,values):
  shape=super()._shape(path,values)
  f,v=read_wave(path/'raw/ac.ac',{'VOP','VOM'});h=v['VOP']-v['VOM'];db=20*np.log10(abs(h));fc=values.get('Filter_cutoff_Hz')
  if fc and fc*30<f[-1]:
   shape['slope_3fc_to_30fc_dB_dec']=float(np.interp(np.log(30*fc),np.log(f),db)-np.interp(np.log(3*fc),np.log(f),db))
  shape['reconstruction']='four capacitor-loaded OTA stages with physical diode-inverter damping'
  shape['paper_exact']=False
  shape['no_ideal_signal_path_elements']=True
  shape['strict_shape_screen']=bool(shape['falling_relative_3dB_crossings']==1 and shape['rising_relative_3dB_crossings']==0 and shape['peaking_above_dc_dB']<.5 and shape.get('slope_3fc_to_30fc_dB_dec',0)<-60)
  opp=dc(path/'raw/dcOp.dc');keep={k:v for k,v in opp.items() if k in ['VOP','VOM','VIP','VIM','DUT.AP','DUT.AM','DUT.BP','DUT.BM','DUT.DP','DUT.DM']}
  work.dump(path.parent/'dc_nodes.json',keep)
  # Retain compact pole data for independent checking; do not assert stability until parsed.
  for p in (path/'raw').glob('poles*'):
   if p.is_file():shutil.copy2(p,path.parent/p.name)
  return shape

TASK=Task()

def run(label,d,full=False,keep_raw=False):
 guard();suffix=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()[:12]
 label=label+'_'+suffix;dest=ROOT/'trials'/label;raw=RAW/label
 if (dest/'evaluation.json').exists():
  old=json.loads((dest/'evaluation.json').read_text())
  assert old['design']==d and old['full']==full
  for row in old['corners']:
   corner=next(c for c in work.CONDITIONS if c['id']==row['id'])
   for job,deck in TASK.corner_decks(d,corner).items():
    if row['diagnostics']['jobs'][job]['deck_sha256']!=hashlib.sha256(deck.encode()).hexdigest():
     raise RuntimeError('Cached recipe differs; use a new trial label')
  # Measurements are reusable; acceptance must follow the current authorized policy.
  if full:old['grade']=work.grade(old['corners'])
  old['acceptance_limits']={k:dict(lower=v[0],upper=v[1]) for k,v in work.LIMITS.items()}
  return old
 if raw.exists() and any(raw.iterdir()):raise RuntimeError('Existing incomplete trial '+str(raw))
 work.dump(dest/'design.json',d)
 conditions=work.CONDITIONS if full else [work.NOM]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3 if full else 1) as pool:
  rows=list(pool.map(lambda c:TASK.evaluate_corner(d,c,raw/c['id'],keep_raw=keep_raw,timeout=120,deadline=time.monotonic()+150),conditions))
 # Copy small evidence only; raw stays on SSD2 when retained.
 shutil.copytree(raw,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('raw'))
 e=dict(label=label,design=d,full=full,corners=rows,paper_exact=False,golden_verified=False)
 e['acceptance_limits']={k:dict(lower=v[0],upper=v[1]) for k,v in work.LIMITS.items()}
 if full:e['grade']=work.grade(rows)
 work.dump(dest/'evaluation.json',e)
 print(label,[(r['id'],r['values'],r['diagnostics'].get('filter_response',{}).get('strict_shape_screen')) for r in rows],flush=True)
 return e

if __name__=='__main__':
 d=json.loads((ROOT.parent/'starting_design.json').read_text());d.update(cap_b_F=2e-12,cap_d_F=2e-12,damping_ratio=1.)
 run('physical_ac',d,keep_raw=False)
