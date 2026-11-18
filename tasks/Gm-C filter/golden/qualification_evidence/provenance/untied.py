"""More sizing freedom in the SAME OTA connectivity; symmetric signal pairs remain tied."""
import re
from compact import CompactTask
from engine import mutate

SPLITS={'M19':'cm_node_n','M23':'cm_node_n','M20':'cm_node_p','M24':'cm_node_p','M25':'bias_n','M28':'bias_p'}

class UntiedTask(CompactTask):
 def __init__(self):
  super().__init__()
  base={v['name']:v for v in self.variables}
  self.extra_variables=[]
  for device,group in SPLITS.items():
   for par in ('w','l'):
    parent=base[group+'_'+par]
    self.extra_variables.append(dict(name=device+'_'+par,lower=parent['lower'],upper=parent['upper']))

 def corner_decks(self,design,corner):
  d=dict(design);changes={}
  for device,group in SPLITS.items():
   changes[device]={p:d.pop(device+'_'+p,d[group+'_'+p]) for p in ('w','l')}
  for v in self.extra_variables:
   dev,p=v['name'].split('_');x=changes[dev][p]
   if not v['lower']<=x<=v['upper']:raise ValueError('Out of bounds '+v['name'])
  decks=super().corner_decks(d,corner)
  for job,deck in decks.items():
   before=re.findall(r'(?m)^(M\w+) (\([^\n]+\))',deck)
   deck=mutate(deck,{cell:changes for cell in ('ota_fig2_interpreted','ota_fig2_literal')})
   assert before==re.findall(r'(?m)^(M\w+) (\([^\n]+\))',deck),'Connectivity changed'
   decks[job]=deck
  return decks

def expand(d):
 d=dict(d)
 for device,group in SPLITS.items():
  for p in ('w','l'):d[device+'_'+p]=d[group+'_'+p]
 return d
