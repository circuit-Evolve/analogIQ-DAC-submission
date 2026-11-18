from pathlib import Path
import sys, json, hashlib, shutil, csv, time, os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import least_squares, differential_evolution
from scipy.stats import qmc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import mutate, execute, read_wave
P=Path(__file__).resolve().parent; BASE=P.parent; S=Path('<WORK>/four_papers_20261109/fgmos_full_wave_rectifier/sizing')
BASEDECK=(BASE/'netlists/DC_AC_tb/spectre/schematic/netlist/input.scs').read_text().replace('\\\n',' '); BASEDECK=BASEDECK[:BASEDECK.index('simulatorOptions')]
GROUPS=[('inputdiode',['M3','M5']),('inputcascode',['M4','M6']),('bias1',['M1']),('bias2',['M2']),('sumsink',['M9','M10']),('feedback',['M11']),('pmirror',['M12','M13']),('output',['M14']),('fgpair',['MP'])]
NAMES=[n+'_W_um' for n,g in GROUPS]+['input_L_um','bias_L_um','sink_L_um','pmirror_L_um','fg_L_um','coupling_C_fF']
X0=np.log([16,16,16,16,16,16,16,45,16,.18,.18,.18,.18,.18,100.])
LO=np.log([.5]*9+[.18]*5+[10]); HI=np.log([500]*9+[3]*5+[1e5])
CONDS=[('NN',27),('FF',27),('SS',27),('FS',27),('SF',27),('NN',-27),('NN',0),('NN',100)]
TARGET=np.array([1.88,115.4,17.37]);COUNT=0;BEST=1e99

def deck(x,co='NN',temp=27,full=False):
 v=np.exp(x); ch={'fwr_fig4':{},'fgpmos':{}}
 for i,(_,names) in enumerate(GROUPS):
  for name in names:
   cell='fgpmos' if name=='MP' else 'fwr_fig4'
   li=9 if i in [0,1] else 10 if i in [2,3] else 11 if i in [4,5,7] else 12 if i==6 else 13
   ch[cell][name]={'w':v[i]*1e-6*(2 if name=='M10' else 1),'l':v[li]*1e-6}
 if len(v)>15:ch['fwr_fig4']['M13']['w']=v[15]*1e-6
 ch['fgpmos'].update({c:{'c':v[14]*1e-15} for c in ['C1','C2']})
 s=mutate(BASEDECK,ch).replace('section=NN','section='+co)
 s+=f'simulatorOptions options reltol=1e-6 vabstol=1e-9 iabstol=1e-15 temp={temp} tnom=27 gmin=1e-15 maxwarns=20\nsaveOptions options save=selected currents=selected\nsave OUT_SRC:p VDD_SRC:p VBIAS_SRC:p\n'
 s+='dcOp dc\ndc dc dev=IIN param=dc start=-35u stop=35u step='+('.25u' if full else '2.5u')+'\nac ac start=10 stop=1G dec='+('100' if full else '25')+'\n'
 return s

def measure(d):
 x,v=read_wave(d/'raw/dc.dc');y=-v['OUT_SRC:p'];pv=-.7*v['VDD_SRC:p'];pt=pv-.2*v['VBIAS_SRC:p']-.7*v['OUT_SRC:p'];iz=np.argmin(abs(x));err=100*np.max(abs(y-abs(x)))/35e-6
 f,a=read_wave(d/'raw/ac.ac');h=-a['OUT_SRC:p'];g=20*np.log10(np.maximum(abs(h),1e-300));idx=np.where(g<=g[0]-3)[0];bw=1e9
 if len(idx) and idx[0]>0:
  k=idx[0];bw=10**np.interp(g[0]-3,g[k-1:k+1][::-1],np.log10(f[k-1:k+1])[::-1])
 m={'static_vdd_power_uW':float(pv[iz]*1e6),'max_vdd_power_uW':float(max(pv)*1e6),'ac_bandwidth_MHz':float(bw/1e6),'max_deviation_fullscale_percent':float(err),'ac_low_frequency_gain_dB':float(g[0]),'static_total_external_power_uW':float(pt[iz]*1e6),'max_total_external_power_uW':float(max(pt)*1e6)}
 return m,(x,y,pv,pt),(f,g,np.angle(h,deg=True))

def residual(m):
 a=np.array([m[k] for k in ['static_vdd_power_uW','max_vdd_power_uW','ac_bandwidth_MHz']]);r=np.log(np.maximum(a,1e-12)/TARGET)
 return np.r_[r,max(0,m['max_deviation_fullscale_percent']-8)/25]

def run(x,co='NN',temp=27,full=False,keep=None):
 global COUNT
 key=hashlib.sha256((np.asarray(x).tobytes()+f'{co}{temp}{full}'.encode())).hexdigest()[:20];d=S/key
 if (d/'metrics.json').exists():m=json.loads((d/'metrics.json').read_text())
 else:
  rc=execute(deck(x,co,temp,full),d,timeout=30)
  COUNT+=1
  if rc: return {'failed':rc}
  try:m,dc,ac=measure(d)
  except Exception as e:return {'failed':str(e)}
  m.update(corner=co,temp_C=temp);(d/'metrics.json').write_text(json.dumps(m,indent=2))
 if keep:
  keep=Path(keep);keep.mkdir(parents=True,exist_ok=True)
  m,dc,ac=measure(d);m.update(corner=co,temp_C=temp)
  for f in ['input.scs','spectre.log','stdout.log','metrics.json']:shutil.copy2(d/f,keep/f)
  for name,header,arr in [('dc_transfer.csv',['Iin_A','Iout_A','VDD_power_W','total_external_power_W'],dc),('ac_response.csv',['frequency_Hz','gain_dB','phase_deg'],ac)]:
   with (keep/name).open('w') as f:w=csv.writer(f);w.writerow(header);w.writerows(zip(*arr))
 return m

def objective(x,conds=CONDS[:1],stage='nominal'):
 global BEST
 with ThreadPoolExecutor(max_workers=4) as pool: ms=list(pool.map(lambda c:run(x,*c),conds))
 if any('failed' in m for m in ms):r=np.ones(len(conds)*4)*100
 else:r=np.concatenate([residual(m) for m in ms])
 score=float(np.mean(r*r)); rec={'stage':stage,'score':score,'x':list(x),'params':dict(zip(NAMES,map(float,np.exp(x)))),'metrics':ms}
 with (P/'history.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 if score<BEST:
  BEST=score;(P/(stage+'_best.json')).write_text(json.dumps(rec,indent=2));print('BEST',stage,COUNT,score,[{k:round(v,4) for k,v in m.items() if isinstance(v,float)} for m in ms],flush=True)
 return r

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'broad'
 if mode=='test':
  t=time.time();print(run(X0,full=True,keep=P/'initial_nominal'));print('time',time.time()-t)
 elif mode=='broad':
  objective(X0)
  # 180 deterministic Latin hypercube candidates, then bounded local multistart.
  samples=qmc.LatinHypercube(d=len(X0),seed=20261109).random(180)
  # Physically useful initial region before the wider search.
  lo=np.log([4]*9+[.18]*5+[30]);hi=np.log([200]*9+[1.5]*5+[30000])
  for x in lo+samples*(hi-lo):objective(x)
  rows=[json.loads(l) for l in (P/'history.jsonl').read_text().splitlines()]; rows.sort(key=lambda r:r['score'])
  for i,r in enumerate(rows[:5]):
   res=least_squares(lambda x:objective(x,stage='nominal'),r['x'],bounds=(LO,HI),diff_step=.005,max_nfev=90,ftol=2e-5,xtol=2e-5,gtol=2e-5)
 elif mode=='robust':
  x=np.array(json.loads((P/'nominal_best.json').read_text())['x']);objective(x,CONDS,stage='robust')
  res=least_squares(lambda x:objective(x,CONDS,stage='robust'),x,bounds=(LO,HI),diff_step=.0005,max_nfev=45,ftol=2e-5,xtol=2e-5,gtol=2e-5)
 elif mode=='verify':
  best=json.loads((P/'robust_best.json').read_text());out=[]
  for c,t in CONDS:out.append(run(best['x'],c,t,full=True,keep=P/'best_verified'/f'{c}_{t}'))
  (P/'verified_results.json').write_text(json.dumps(out,indent=2))
