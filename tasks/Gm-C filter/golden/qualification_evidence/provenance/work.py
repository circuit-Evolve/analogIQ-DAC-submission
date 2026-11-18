"""Private Gm-C audit; separate P/V/T sweeps, never writes AnalogIQ."""
from pathlib import Path
import sys, json, math, shutil, hashlib, concurrent.futures, argparse
import numpy as np
ROOT=Path(__file__).resolve().parent
OLD=Path('<WORK>/ledro8h_four_corners_20261109T060146Z')
PACK=OLD/'pack'
RAW=Path('<WORK>/four_papers_20261109/gmc_individual_15pct_20261112')
sys.path.insert(0,str(PACK))
from gm_c_corners import Task

LIMITS={
 'OTA_differential_gain_dB':(33.15,None,39),
 'OTA_unity_gain_frequency_Hz':(8.5e9,None,1e10),
 'OTA_phase_margin_deg':(67.15,90.85,79),
 'OTA_common_mode_gain_dB':(None,-20.4,24),
 'Filter_cutoff_Hz':(10e6,20e6,15e6),
 'Filter_input_noise_nV_sqrtHz':(None,97.75,85),
}
TASK=Task()
CONDITIONS=[c for c in TASK.cfg['conditions'] if sum([c['process']!='NN',c['supply_V']!=1.,c['temperature_C']!=27])<=1]
IDS={c['id'] for c in CONDITIONS}
NOM=next(c for c in CONDITIONS if c['nominal'])
assert len(CONDITIONS)==9 and len(IDS)==9

def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n');temp.replace(p)

def grade(rows):
 by={r['id']:r for r in rows};counts={m:0 for m in LIMITS};corners={};loss=0.;missing=0
 for c in CONDITIONS:
  r=by.get(c['id'],{});valid=r.get('execution_ok',False) and not r.get('diagnostics',{}).get('errors',{})
  passed={}
  for m,(lo,hi,scale) in LIMITS.items():
   v=r.get('values',{}).get(m)
   ok=valid and isinstance(v,(float,int)) and math.isfinite(v)
   if not ok:short=100.;missing+=1
   else:short=max(0.,(lo-v)/scale if lo is not None else 0.,(v-hi)/scale if hi is not None else 0.)
   passed[m]=bool(ok and short==0);counts[m]+=passed[m];loss+=math.log1p(short)
  corners[c['id']]=passed
 return dict(all_pass=sum(all(v.values()) for v in corners.values()),scalar_pass=sum(counts.values()),total_corners=9,total_tests=54,loss=loss,missing=missing,metric_pass_counts=counts,corner_pass= corners)

def regrade():
 ranked=[]
 for p in sorted((OLD/'gm_c/sim').glob('e*/evaluation.json')):
  data=json.loads(p.read_text());rows=data.get('corners',[])
  if not IDS.issubset({r['id'] for r in rows}):continue
  g=grade(rows)
  ranked.append(dict(source=str(p),evaluation=p.parent.name,**g))
 ranked.sort(key=lambda x:(-x['all_pass'],-x['scalar_pass'],x['loss']))
 dump(ROOT/'legacy_regraded.json',ranked)
 p=Path(ranked[0]['source']);design=json.loads((p.parent/'adapter_design.json').read_text())['parameters']
 TASK.nominal.decks(design)
 dump(ROOT/'starting_design.json',design)
 dump(ROOT/'conditions.json',CONDITIONS)
 dump(ROOT/'target_policy.json',dict(tolerance=.15,limits={k:dict(lower=v[0],upper=v[1]) for k,v in LIMITS.items()},phase_margin_scope='Existing unity-feedback estimate; loop stability not yet verified',noise_frequency_Hz=1e6,noise_frequency_is_assumed=True))
 for r in ranked[:5]:print({k:r[k] for k in ['evaluation','all_pass','scalar_pass','loss','metric_pass_counts']},flush=True)

def run_corner(design,c,label):
 out=RAW/label/c['id'];dest=ROOT/'trials'/label/c['id']
 if (dest/'results.json').exists():
  cached=json.loads((dest/'results.json').read_text())
  for job,deck in TASK.corner_decks(design,c).items():
   expected=hashlib.sha256(deck.encode()).hexdigest()
   if cached['diagnostics']['jobs'][job]['deck_sha256']!=expected:
    raise RuntimeError('Cached deck differs from requested sizing/condition '+str(dest))
  return cached
 if out.exists() and any(out.iterdir()):raise RuntimeError('Refusing to overwrite incomplete trial '+str(out))
 r=TASK.evaluate_corner(design,c,out,keep_raw=False,timeout=180)
 response=np.loadtxt(out/'filter_response.csv',delimiter=',',skiprows=1)
 extra={str(f):float(np.interp(np.log(f),np.log(response[:,0]),response[:,1])) for f in [1,1e3,1e6,12.75e6,15e6,17.25e6,100e6,1e9]}
 r['diagnostics']['gain_at_frequency_dB']=extra
 dump(out/'results.json',r)
 shutil.copytree(out,dest)
 return r

def run(label,design,conditions=None):
 conditions=conditions or CONDITIONS
 TASK.nominal.decks(design)
 design_path=ROOT/'trials'/label/'design.json'
 if design_path.exists() and json.loads(design_path.read_text())!=design:
  raise RuntimeError('Refusing to reuse a trial label for different sizing: '+label)
 dump(design_path,design)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  rows=list(pool.map(lambda c:run_corner(design,c,label),conditions))
 result=dict(design=design,conditions=conditions,corners=rows)
 if len(conditions)==9:result['grade']=grade(rows)
 dump(ROOT/'trials'/label/'evaluation.json',result)
 print(label,result.get('grade',{}),flush=True)
 return result

def baseline_and_caps():
 design=json.loads((ROOT/'starting_design.json').read_text())
 run('baseline',design)
 # Sizing-only diagnostic: same geometry and bias, vary only the existing capacitors.
 for cap in [1e-13,1e-12,1e-11,1e-10,1e-9,1e-8]:
  d=dict(design,cap_b_F=cap,cap_d_F=cap)
  run('caps_'+format(cap,'.0e'),d,[NOM])
 rows=[]
 for p in sorted((ROOT/'trials').glob('*/evaluation.json')):
  e=json.loads(p.read_text())
  r=next(r for r in e['corners'] if r['id']==NOM['id'])
  rows.append(dict(label=p.parent.name,cap_b_F=e['design']['cap_b_F'],cap_d_F=e['design']['cap_d_F'],values=r['values'],shape=r['diagnostics'].get('filter_response'),gain_at_frequency_dB=r['diagnostics'].get('gain_at_frequency_dB')))
 dump(ROOT/'nominal_capacitor_audit.json',rows)
 print(json.dumps(rows,indent=2),flush=True)

if __name__=='__main__':
 action=sys.argv[1]
 if action=='regrade':regrade()
 elif action=='baseline':baseline_and_caps()
