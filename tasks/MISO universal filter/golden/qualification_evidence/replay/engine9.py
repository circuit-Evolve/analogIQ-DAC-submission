from pathlib import Path
import sys,json,math,re,hashlib,time,concurrent.futures,tarfile,shutil
import numpy as np
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B/'pack'))
from miso_corners import Task as BaseTask
from miso_engine import execute,read_wave,dc
from physical import enable_tail_override,enable_resistor_override,enable_input_multiplicity,enable_pmirror_multiplicity,enable_front_output_multiplicity,enable_A1_ota_override,enable_R1_multiplicity,enable_ndiode_override
POLICY=json.loads((B/'policy.json').read_text());NAMES=[c['metric'] for c in POLICY];assert len(NAMES)==9
class Task(BaseTask):
 def __init__(self,d=None,ac_points=150):
  if ac_points not in [150,300,600,1200]:raise ValueError('Unsupported numerical AC grid')
  self.ac_points=ac_points
  super().__init__('nine_full');assert self.cfg['constraints']==POLICY;self.profile='nine_full';self._budget_seconds=lambda:3600.0
  for v in self.variables:
   k=v['name']
   if k=='VBIAS':v['upper']=.6
   if k in ['C1','C2']:v['lower']=1e-12;v['upper']=200e-12
   if k=='R3':v['upper']=75000
   if k=='OTA_IBIAS':v['upper']=500e-6
   if k.startswith(('frontend_','ota_','resistor_')) and k.endswith(('_w','_l')):
    v['lower']=.4e-6 if k.endswith('_w') else .18e-6;v['upper']=100e-6 if k.endswith('_w') else 20e-6
  d=d or {}
  if any(k.startswith('M25_') for k in d):enable_tail_override(self)
  if any(k.startswith('R2_') for k in d):enable_resistor_override(self)
  if 'OTA_input_m' in d:enable_input_multiplicity(self)
  if 'OTA_pmirror_m' in d:enable_pmirror_multiplicity(self)
  if 'frontend_output_m' in d:enable_front_output_multiplicity(self)
  if 'R1_m' in d:enable_R1_multiplicity(self)
  if any('ota_ndiode_' in k for k in d):enable_ndiode_override(self)
  if any(k.startswith('A1_') for k in d):enable_A1_ota_override(self)
  original_decks=self.decks
  def numerical_decks(design):
   decks=original_decks(design)
   if self.ac_points!=150 and 'VM_BP' in decks:
    decks['VM_BP'],n=re.subn(r'(?m)^(ac ac [^\n]*\bdec=)\S+',lambda m:m[1]+str(self.ac_points),decks['VM_BP']);assert n==1
   return decks
  self.decks=numerical_decks
 def extract(self,paths):
  values,diag=super().extract(paths)
  diag['unscored_building_block_diagnostics']={k:v for k,v in values.items() if k not in NAMES}
  diag['measurement_profile']='nine_user_retained_scalars_same_original_definitions'
  return {k:values.get(k) for k in NAMES},diag

def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False))
def grade(rows):
 result=[]
 for r in rows:
  cs=[]
  for c in POLICY:
   v=r['values'].get(c['metric']);valid=r.get('execution_ok') is True and isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
   yes=valid and (c.get('lower') is None or v>=c['lower']) and (c.get('upper') is None or (v<c['upper'] if c.get('upper_exclusive') else v<=c['upper']))
   p=10 if not valid or v<0 else (math.log(c['lower']/max(v,1e-30)) if c.get('lower',0)>v else max(0,math.log(v/c['upper'])) if c.get('upper') is not None and v>0 else 0)
   cs.append({'metric':c['metric'],'value':v if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) else None,'lower':c.get('lower'),'upper':c.get('upper'),'upper_exclusive':c.get('upper_exclusive',False),'passed':yes,'violation':p})
  result.append({'corner':r.get('id',r.get('corner')),'execution_ok':r.get('execution_ok') is True,'checks':cs,'passed':sum(c['passed'] for c in cs),'total':len(cs)})
 ps=[c['violation'] for r in result for c in r['checks']]
 return {'corners':result,'passed':sum(c['passed'] for c in result),'total':len(result)*len(POLICY),'complete_corners':sum(c['passed']==len(POLICY) for c in result),'worst_violation':max(ps,default=10),'squared_violation':sum(p*p for p in ps),'expected_corner_coverage':len(result)==5 and {r['corner'] for r in result}=={'TT','FF','SS','SF','FS'},'golden':len(result)==5 and {r['corner'] for r in result}=={'TT','FF','SS','SF','FS'} and all(r['execution_ok'] and r['passed']==len(POLICY) for r in result)}

def validate_label(label):
 if not isinstance(label,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*",label) or label in (".",".."):raise ValueError("Unsafe evaluationlabel")
 return label

def full(label,d,workers=4,ac_points=150):
 validate_label(label)
 T=Task(d,ac_points=ac_points);T.max_workers=workers;T.decks(d);r=T.evaluate(d,B/'full'/label,keep_raw=True,timeout=180);g=grade(r['corners']);g.update(label=label,design=d,evidence=str(B/'full'/label),numerical_profile={'VM_BP_AC_points_per_decade':ac_points,'frequency_expression':next(c['expression'] for c in POLICY if c['metric']=='MISO_BP_frequency'),'other_measurements':'unchanged original definitions and stimuli'});write(B/(label+'_full.json'),g);print('FULL',label,g['passed'],g['total'],g['complete_corners'],g['worst_violation'],flush=True);return g

def ac_screen(label,d,corners=('TT','FF','SS','SF','FS'),workers=4,ac_points=150):
 validate_label(label)
 T=Task(d,ac_points=ac_points);decks=T.decks(d);out=B/'ac_screens'/label
 design_hash=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest();deck_hash=hashlib.sha256(decks['VM_BP'].encode()).hexdigest()
 if (out/'summary.json').exists():
  cached=json.loads((out/'summary.json').read_text())
  if cached.get('design_hash')!=design_hash or cached.get('base_deck_hash')!=deck_hash or set(cached.get('corners_requested',[]))!=set(corners):raise FileExistsError('Refusingstalescreenlabel '+label)
  return cached
 def one(c):
  folder=out/c['id'];s=decks['VM_BP'].replace('section=NN','section='+c['model_section']);rc=execute(s,folder,timeout=60);v={};errors=[]
  if rc==0:
   try:
    x,y=read_wave(folder/'raw/ac.ac',['VOUT']);a=np.abs(y['VOUT']);dy=np.gradient(a,x);hits=np.flatnonzero((dy[:-1]>=0)&(dy[1:]<0));peak=None
    if len(hits):j=int(hits[0]);peak=float(np.exp(np.interp(0,[dy[j+1],dy[j]],[np.log(x[j+1]),np.log(x[j])])))
    xx,n=read_wave(folder/'raw/noise.noise',['in','out']);op=dc(folder/'raw/dcOp.dc')
    v={'frequency_screen_Hz':peak,'power_screen_W':.9*(-op['VDD_SRC:p']+op['VSS_SRC:p']),'BP_noise_in':float(np.interp(3.98e6,xx,n['in'])),'BP_noise_out':float(np.interp(3.98e6,xx,n['out'])),'gain_at_3p98MHz':float(np.interp(3.98e6,x,a))}
   except Exception as exc:errors.append(str(exc))
  r={'corner':c['id'],'execution_ok':rc==0 and not errors,'returncode':rc,'values':v,'errors':errors,'deck_sha256':hashlib.sha256(s.encode()).hexdigest()};write(folder/'screen.json',r);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:rs=list(pool.map(one,[c for c in T.corners if c['id'] in corners]))
 score=0;passed=0;fs=[]
 for r in rs:
  for k,lo,hi in [('frequency_screen_Hz',3.383e6,4.577e6),('power_screen_W',0,5.3935e-3),('BP_noise_in',0,75.946e-9),('BP_noise_out',0,65.366e-9)]:
   v=r['values'].get(k)
   if not r['execution_ok'] or v is None or not math.isfinite(v) or v<0:score+=100;continue
   p=max(0,math.log(lo/max(v,1e-30)) if lo else 0,math.log(v/hi) if v else 0);score+=p*p;passed+=p==0
  if r['values'].get('frequency_screen_Hz'):fs.append(r['values']['frequency_screen_Hz'])
 res={'label':label,'AC_points_per_decade':ac_points,'design':d,'design_hash':design_hash,'base_deck_hash':deck_hash,'corners_requested':list(corners),'corners':rs,'score':score,'screen_passed':passed,'screen_total':len(rs)*4,'frequency_ratio':max(fs)/min(fs) if len(fs)==len(rs) else None,'scope':'ACscreenonly; derivativefrequency approximation andVM_BPDCpower areNOTacceptedfullmeasurements'};write(out/'summary.json',res);return res


def valid_full(g):
 return g.get('expected_corner_coverage') is True and g.get('total')==45 and all(c.get('execution_ok') is True and len(c.get('checks',[]))==9 and {x['metric'] for x in c['checks']}==set(NAMES) and all(isinstance(x.get('value'),(int,float)) and not isinstance(x.get('value'),bool) and math.isfinite(x['value']) for x in c['checks']) for c in g['corners'])

def gain_screen(label,d,workers=4):
 validate_label(label);T=Task(d);decks=T.decks(d);root=B/'gain_screens'/label
 def one(item):
  c,metric,job,sig=item;out=root/c['id']/job;s=decks[job].replace('section=NN','section='+c['model_section']);rc=execute(s,out,timeout=60);value=None
  if rc==0:
   try:value=float(abs(read_wave(out/'raw/ac.ac',[sig])[1][sig][0]))
   except Exception:pass
  con=next(x for x in POLICY if x['metric']==metric);passed=rc==0 and value is not None and math.isfinite(value) and con['lower']<=value<=con['upper'];return {'corner':c['id'],'metric':metric,'value':value,'passed':passed,'returncode':rc}
 jobs=[(c,k,'CORE_'+k.split('_')[0],'ZP_SRC:p' if k=='IZP_gain' else 'X') for c in T.corners for k in ['Y1_gain','Y2_gain','IZP_gain']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(one,jobs))
 r={'label':label,'design':d,'checks':rows,'passed':sum(x['passed'] for x in rows),'total':len(rows)};write(root/'summary.json',r);return r
