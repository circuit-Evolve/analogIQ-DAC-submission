from pathlib import Path
import re,json,subprocess,os,signal,hashlib,time
import numpy as np
ROOT=Path(__file__).resolve().parent;W=ROOT.parent
NUM={'':1,'u':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'k':1e3,'m':1e-3,'meg':1e6}
def num(s):
 m=re.fullmatch(r'([\d.eE+\-]+)([a-zA-Z]*)',s);return float(m[1])*NUM[m[2].lower()]
def clean(s):
 s=s.replace('\\\n',' ')
 s='\n'.join(l for l in s.splitlines() if not any(l.startswith(n) for n in ['dcOpInfo ','modelParameter ','element ','outputParameter ','designParamVals ','primitives ','subckts ']))+'\n'
 s=re.sub(r'sensfile="[^"]+"','sensfile="sens.output"',s)
 return s
def mutate(s,changes):
 # Keys cell/device/parameter; rebuild diffusion geometry consistently with W changes.
 for cell,devs in changes.items():
  m=re.search(r'(?m)^subckt '+cell+r' .*?\n(.*?)^ends '+cell,s,re.S);assert m,cell;body=m[1]
  for name,updates in devs.items():
   mdev=re.search(r'(?m)^\s*'+re.escape(name)+r' \([^\n]+\) [^\n]+',body);assert mdev,(cell,name)
   line=mdev[0];old=dict(re.findall(r'(\w+)=(\S+)',line));new=dict(updates)
   if 'w' in new:
    wo=num(old['w']);wn=float(new['w'])
    for p in ['as','ad']:
     if p in old:new[p]=num(old[p])*wn/wo
    for p in ['ps','pd']:
     if p in old:new[p]=max(2*wn+num(old[p])-2*wo,2*wn)
   for k,v in new.items():
    value=f'{float(v):.12g}';line,n=re.subn(r'\b'+k+r'=\S+',k+'='+value,line);assert n==1,(name,k)
   body=body[:mdev.start()]+line+body[mdev.end():]
  s=s[:m.start(1)]+body+s[m.end(1):]
 return s
def execute(s,d,timeout=12,fmt='psfascii'):
 d=Path(d);d.mkdir(parents=True,exist_ok=True);(d/'input.scs').write_text(s)
 with (d/'stdout.log').open('w') as f:
  p=subprocess.Popen(['/opt/cadence/bin/spectre','input.scs','-format',fmt,'-raw','raw','+log','spectre.log'],cwd=d,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:rc=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   try:os.killpg(p.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    p.wait(timeout=5)
   rc=124
 (d/'status.json').write_text(json.dumps({'returncode':rc,'nominal_only':True}));return rc
FLOAT=r'[-+\d.eE]+'
def dc(p):
 s=Path(p).read_text();s=s[s.index('VALUE'):];return {m[1]:float(m[2]) for m in re.finditer(r'^"([^"]+)" "[VI]" ('+FLOAT+r')',s,re.M)}
def read_wave(p,signals=None):
 data={};x=[];active=False
 with Path(p).open() as f:
  for line in f:
   if not active:
    if line.startswith('VALUE'):active=True
    continue
   if not line.startswith('"'):continue
   name,_,val=line[1:].partition('" ');val=val.strip()
   if name in ['freq','time','dc']:
    x.append(float(val));continue
   if signals is not None and name not in signals:continue
   if val.startswith('"V" ') or val.startswith('"I" '):val=val[4:]
   if val.startswith('('):
    a=re.findall(FLOAT,val);v=complex(float(a[0]),float(a[1]))
   else:
    try:v=float(val.split()[0])
    except ValueError:continue
   data.setdefault(name,[]).append(v)
 return np.array(x),{k:np.array(v) for k,v in data.items()}
def cp_metrics(v):
 def get(n):return v.get(n+':d',v.get(n+':1'))
 iu=-get('DUT.T2')*1e6;idn=get('DUT.T3')*1e6;it=-v['VDD_SRC:p']*1e6
 return {'IUP_uA':iu,'IDN_uA':idn,'Total_supply_current_uA':it,'Mismatch_paper_percent':100*abs(iu-idn)/abs(it),'Supply_power_uW':1.2*it,'PG_V':v['DUT.PG'],'REPL_V':v['DUT.REPL'],'DNMID_V':v['DUT.DNMID']}
