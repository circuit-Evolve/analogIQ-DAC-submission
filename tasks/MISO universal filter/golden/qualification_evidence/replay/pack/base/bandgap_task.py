from pathlib import Path
import json,re,math
import numpy as np
from engine import clean,mutate,dc,read_wave
P=Path(__file__).resolve().parent
class Task:
 def __init__(self,profile='search_full'):
  self.profile=profile;self.cfg=json.loads((P/'bandgap.json').read_text());self.variables=self.cfg['variables'];self.templates=P/'templates/bandgap'
 def paper_design(self):return json.loads((P/'bandgap_paper_seed.json').read_text())['parameters']
 def decks(self,design):
  from judge import validate_design
  validate_design(self.variables,design)
  if design==self.paper_design():return {n:(self.templates/(n+'.scs')).read_text() for n in ['nominal','line','temperature']}
  changes={}
  for v in self.variables:
   value=design[v['name']]*(1e6 if v['parameter'] in ['w','l'] else 1)
   for name in v['devices']:changes.setdefault(v['cell'],{}).setdefault(name,{})[v['parameter']]=value
  return {n:mutate(clean((self.templates/(n+'.scs')).read_text()),changes) for n in ['nominal','line','temperature']}
 def plan_text(self):
  deck=clean((self.templates/'nominal.scs').read_text());s=re.search(r'(?ms)^subckt bgr_fig3_paper .*?^ends bgr_fig3_paper',deck)[0]
  for v in self.variables:
   for name in v['devices']:
    value='(<'+v['name']+'>*1e6)' if v['parameter'] in ['w','l'] else '<'+v['name']+'>'
    pattern=r'(?m)^(\s*'+re.escape(name)+r' \([^\n]+\) [^\n]*?\b'+v['parameter']+r'=)\S+'
    s,n=re.subn(pattern,lambda m:m[1]+value,s);assert n==1,(name,v['parameter'])
  return '// SKY130 W/L are micron-native in netlist: variables are SI meters, converted by 1e6.\n'+s
 def extract(self,paths):
  vals={c['name']:None for c in self.cfg['constraints']};diag={'assumptions':json.loads((P/'bandgap_paper_seed.json').read_text())['assumptions'],'errors':{}};v=None
  if 'nominal' in paths:
   p=paths['nominal']/'raw'
   try:
    v=dc(p/'dcOp.dc');vals['Vref_V']=v['VREF']
    f,a=read_wave(p/'ac.ac',{'VREF'});assert len(f)>0 and abs(f[0]-1)<1e-8;vals['PSRR_LF_dB']=float(-20*np.log10(abs(a['VREF'][0])))
   except Exception as e:diag['errors']['nominal_dc_ac']=str(e)
   try:
    t,a=read_wave(p/'tran.tran.tran',{'VREF','VDD_SRC:p'});assert t[-1]>=30e-6*(1-1e-8)
    integrate=getattr(np,'trapezoid',None) or np.trapz;vals['Power_uW']=float(-1.8*integrate(a['VDD_SRC:p'],t)/(t[-1]-t[0])*1e6);diag['steady_output_vpp_V']=float(np.ptp(a['VREF'][t>20e-6]))
   except Exception as e:diag['errors']['nominal_tran']=str(e)
  for name,axis in [('line','VS'),('temperature','temp')]:
   if name not in paths:continue
   try:
    p=paths[name]/'raw/dc.dc';text=p.read_text().split('VALUE',1)[1];x=np.array([float(q) for q in re.findall(r'^"'+axis+r'" (\S+)',text,re.M)]);_,a=read_wave(p,{'VREF'});y=a['VREF'];assert len(x)==len(y)
    if name=='line':
     assert len(x)==91 and abs(x[0]-1.71)<1e-8 and abs(x[-1]-1.89)<1e-8;vals['Line_sensitivity_percent']=float(100*np.ptp(y)/.18)
    else:
     assert len(x)==161 and x[0]==-40 and x[-1]==120
     if v is not None and v['VREF']!=0:vals['TC_19_120_ppm_C']=float(1e6*np.ptp(y[x>=19])/(v['VREF']*101))
   except Exception as e:diag['errors'][name]=str(e)
  return vals,diag
