"""Fixed-topology17MOS high-pass candidate, all12paper corner points."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sys,json,copy,re,math,hashlib,shutil,gzip,time
P=Path(__file__).resolve().parent;B=P/'base';sys.path.insert(0,str(B))
from engine import execute,mutate,num,dc,read_wave
from robust_metrics import hpf_scalars
from dtmos_task import Task as NominalTask
V=Path('<WORK>/four-circuit-corners-20261109/dtmos')
class Task:
 def __init__(self,profile='search_full'):
  self.profile=profile;self.old=NominalTask();self.cfg=copy.deepcopy(self.old.cfg)
  self.base=(P/'dtmos_source_best.scs').read_text()
  self.corner_cfg=json.loads((P/'dtmos_corner_setup.json').read_text());self.corners=self.corner_cfg['corners']
  vars=[]
  for v in self.cfg['variables']:
   v['binding']['instances']=[x for x in v['binding']['instances'] if not x.endswith('_FB')]
   if v['name']=='Mpb78_w':
    for dev in ['Mpb7','Mpb8']:
     q=copy.deepcopy(v);q['name']=dev+'_w';q['binding']['instances']=[dev];vars.append(q)
   else:vars.append(v)
  seed={}
  for v in vars:
   name=v['name'];param=v['binding']['parameter'];dev=v['binding']['instances'][0]
   line=re.search(r'^\s*'+dev+r' \([^\n]+\) [^\n]+',self.base,re.M)[0]
   value=num(re.search(r'\b'+param+r'=(\S+)',line)[1]);value*=2 if dev=='M3' and param=='w' else 1
   seed[name]=value;v['initial']=value;v['provenance']='Frozen198Hz17MOSnominalcandidate; design variables alter sizing only.'
   if name=='Mnb4_w':v['upper']=100e-6
   if name=='Mnb4_l':v['lower']=.18e-6
   if name=='Mnb5_w':v['lower']=.4e-6
   if name=='Mnb5_l':v['upper']=8e-6
   assert v['lower']<=value<=v['upper'],(name,value)
  self.seed=seed;self.cfg['variables']=vars;self.variables=vars
  self.cfg['constraints']=[c for c in self.cfg['constraints'] if not c['name'].startswith('CORE')]
  self.cfg['conditions']=[{**c,'nominal':c['group']=='nominal'} for c in self.corners]
  for c in self.cfg['constraints']:
   c['conditions']=[x['id'] for x in self.corners];c['scope']='Same17MOSphysicalHPF at everypaper operatingpoint';c['aggregate']='worst'
   if c['name']=='HPF_Rail_power_mW':c['recipe']='1000*actual_rail_magnitude_V*(-I(VDD_SRC:p)+I(VSS_SRC:p))'
  self.cfg.update(task_id='dtmos',topology_id='dtmos_verified_17mos_hpf',technology_id='gpdk180_all_paper_corners',description='Current198HzHPFcandidate; original3scalar targets at12paperoperatingpoints. No extra feedback transistors. M2off and fractional-order reproduction remain unverified.',bounds_policy='Prior bounds expanded only to include newseed and retainphysical sizing freedom; Mpb7/Mpb8 widths independent to preserve currentseed. All M3widths totalwithm2.')
  self.cfg.pop('frozen_operating_metadata',None)
  self.cfg['operating_conditions'].update(temperature_C=[-27,0,27,100],rail_magnitude_V=[.7,.8,.9,1.,1.1],transient_maxstep_s=1e-6)
  self.cfg['provenance']=str(P/'dtmos_corner_setup.json')
 def seed_design(self):return dict(self.seed)
 paper_design=seed_design
 def plan_text(self):return '//17MOSfixedtopology; Mnb5userconfirmed; noFBreplicas. Per-devicevariablebindingsinconfig.\n'+self.base
 def deck(self,design,corner):
  changes={}
  for v in self.variables:
   x=design[v['name']]
   if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not v['lower']<=x<=v['upper']:raise ValueError('Invalid '+v['name'])
   if x==self.seed[v['name']]:continue
   for dev in v['binding']['instances']:
    par=v['binding']['parameter'];changes.setdefault(dev,{})[par]=x/2 if dev=='M3' and par=='w' else x
  s=mutate(self.base,{'dtmos_candidate_stb':changes}) if changes else self.base
  s,n=re.subn(r'section=NN\b','section='+corner['process'],s);assert n==1
  for name,value in [('VDD_SRC',corner['rail_magnitude_V']),('VSS_SRC',-corner['rail_magnitude_V'])]:
   s,n=re.subn(r'('+name+r' \([^\n]+\) vsource dc=)\S+',lambda m:m[1]+str(value),s);assert n==1
  s,n=re.subn(r'\btemp=27\b','temp='+str(corner['temperature_C']),s);assert n==1
  assert len(re.findall(r'^\s*M\w+ \(',s,re.M))==17
  assert '_FB' not in s
  return s
 def evaluate(self,design,out,keep_raw=False,timeout=180):
  out=Path(out);out.mkdir(parents=True,exist_ok=True)
  deadline=time.monotonic()+(1800 if self.profile=='full_verify' else 900)
  def one(c):
   d=out/c['id'];s=self.deck(design,c);err=None;remaining=deadline-time.monotonic();launched=remaining>0
   d.mkdir(parents=True,exist_ok=True)
   if not launched:(d/'input.scs').write_text(s);rc=124;err='Overall evaluation deadline reached'
   else:
    try:rc=execute(s,d,timeout=min(timeout,remaining))
    except Exception as e:rc=1;err=repr(e)
   (d/'status.json').write_text(json.dumps({'returncode':rc,'corner':c,'error':err}))
   vals={x['name']:None for x in self.cfg['constraints']};diag={}
   if rc==0:
    try:
     v,z=self.old.extract({'DTMOS_HPF_NOMINAL':d});vals.update({k:v.get(k) for k in vals});diag=z['HPF']
     f,w=read_wave(d/'raw/ac.ac',['VOUT_SENSE:p']);extra=hpf_scalars(f,abs(w['VOUT_SENSE:p']));vals.update(extra);diag['additional_scalars']=extra
     op=dc(d/'raw/dcOp.dc');vals['HPF_Rail_power_mW']=1000*c['rail_magnitude_V']*(-op['VDD_SRC:p']+op['VSS_SRC:p']);diag['rail_power_mW']=vals['HPF_Rail_power_mW'];diag['input_V']=op['IN'];diag['M2_drain_A']=op['DUT.M2:d']
    except Exception as e:err=repr(e)
   result={'id':c['id'],'values':vals,'diagnostics':diag,'execution_ok':rc==0 and err is None,'error':err,'corner':c,'simulator_invocations':int(launched)}
   (d/'corner_metrics.json').write_text(json.dumps(result,indent=2))
   raw=d/'raw'
   if raw.exists():
    if not keep_raw:shutil.rmtree(raw)
    else:
     records=[]
     for p in raw.iterdir():
      if p.is_file() and p.stat().st_size>1000000:
       content=p.read_bytes();q=p.with_name(p.name+'.gz');q.write_bytes(gzip.compress(content,compresslevel=1));assert gzip.decompress(q.read_bytes())==content;records.append({'file':p.name,'gzip':q.name,'sha256':hashlib.sha256(content).hexdigest()});p.unlink()
     (d/'raw_compression.json').write_text(json.dumps(records,indent=2))
   return result
  with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,self.corners))
  return {'corners':rows,'execution_ok':all(x['execution_ok'] for x in rows),'simulator_invocations':sum(x['simulator_invocations'] for x in rows),'physical_validation':'Scalaroptimizationonly. M2bias/fractional-order equivalence notestablished.'}
