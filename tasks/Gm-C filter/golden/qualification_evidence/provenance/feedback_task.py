"""Independent geometry for the EXISTING filter feedback diodes; same nodes/devices/OTA."""
import re
from wide_task import WideTask
class FeedbackTask(WideTask):
 def __init__(self):
  super().__init__();base={v['name']:v for v in self.variables};self.feedback_variables=[]
  for typ in ('n','p'):
   for par in ('w','l'):
    v=base['input_'+typ+'_'+par]
    self.feedback_variables.append(dict(name='feedback_'+typ+'_'+par,lower=v['lower'],upper=v['upper']*(4 if par=='w' else 1)))
 def corner_decks(self,design,corner):
  d=dict(design);geometry={}
  for v in self.feedback_variables:
   name=v['name'];_,typ,par=name.split('_')
   default=max(d['input_'+typ+'_w']*d.get('damping_ratio',1.),1.2e-7 if typ=='n' else 2.36e-7) if par=='w' else d['input_'+typ+'_l']
   value=d.pop(name,default)
   if not v['lower']<=value<=v['upper']:raise ValueError('Out of bounds '+name)
   geometry[name]=value
  decks=super().corner_decks(d,corner)
  for job,deck in decks.items():
   before=re.findall(r'(?m)^(\w+) (\([^\n]+\))',deck)
   def replace(m):
    prefix,typ=m[1],m[2];w=geometry['feedback_'+typ+'_w'];l=geometry['feedback_'+typ+'_l']
    return prefix+f' w={w:.12g} l={l:.12g} m=1 as={w*.28e-6:.12g} ad={w*.28e-6:.12g} ps={2*w+.56e-6:.12g} pd={2*w+.56e-6:.12g}'
   deck,count=re.subn(r'(?m)^(FD[1-4][PM][np] \([^\n]+\) gpdk090_([np])mos1v) .*$',replace,deck)
   assert count==16
   assert re.findall(r'(?m)^(\w+) (\([^\n]+\))',deck)==before,'Connectivity changed'
   decks[job]=deck
  return decks

def expand(d):
 d=dict(d)
 for typ in ('n','p'):
  d['feedback_'+typ+'_w']=max(d['input_'+typ+'_w']*d.get('damping_ratio',1.),1.2e-7 if typ=='n' else 2.36e-7)
  d['feedback_'+typ+'_l']=d['input_'+typ+'_l']
 return d
