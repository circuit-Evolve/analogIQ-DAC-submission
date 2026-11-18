"""Strict standalone reproduction of the measured 12/12 scalar DTMOS candidate.
Default: audit 12 exact decks without Spectre. --simulate: fresh full verification.
"""
from pathlib import Path
import sys,json,re,math,hashlib,argparse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'pack'),str(ROOT/'pack/base')]
from robust_dtmos import Gain200Task
from engine import mutate,num
from corner_judge import aggregate,write

def records(s):
 return {name:{'nodes':tuple(nodes.split()),'model':model,'params':dict(re.findall(r'\b(w|l|m|as|ad|ps|pd)=(\S+)',pars))} for name,nodes,model,pars in re.findall(r'^\s*(M\w+) \(([^\n]+)\) (\w+) ([^\n]+)',s,re.M)}
def connections(s):return {k:(v['nodes'],v['model']) for k,v in records(s).items()}
class FrozenTask(Gain200Task):
 def __init__(self):
  super().__init__()
  for v in self.variables:
   p=v['binding']['parameter']
   if p=='w':v.update(lower=.4e-6,upper=200e-6 if v['name']=='M3_w' else 100e-6)
   elif p=='l':v.update(lower=.18e-6,upper=20e-6)
   elif v['name']=='C1':v['upper']=10e-6
  self.topology=connections(self.base)
 def deck(self,d,c):
  basekeys={v['name'] for v in self.variables};extra=['size_Mpb1_w','size_Mpb2_w','size_Mpb3_w','size_Mpb8_w']
  assert set(d)==basekeys|{'M4_w'}|set(extra),'Missing or unrecognized sizing key'
  assert .4e-6<=d['M4_w']<=100e-6
  s=super().deck(d,c)
  changes={'M4':{'w':d['M4_w']}}
  for dev in ['Mnb3','Mnb4']:changes[dev]={p:d[dev+'_'+p] for p in ['w','l']}
  s=mutate(s,{'dtmos_candidate_stb':changes});changes={}
  for key in extra:
   _,dev,par=key.split('_');w=d[key];assert math.isfinite(w) and w>=.4e-6
   m=math.ceil(w/100e-6);changes[dev]={'w':w/m,'m':m}
  s=mutate(s,{'dtmos_candidate_stb':changes});rr=records(s)
  assert len(rr)==17 and connections(s)==self.topology and '_FB' not in s and 'soft_bin' not in s
  for dev,r in rr.items():
   p={k:num(v) for k,v in r['params'].items()}
   assert .4e-6<=p['w']<=100e-6 and .18e-6<=p['l']<=(20e-6 if r['model']=='nmos1' else 40e-6)
   assert p['m']>=1 and p['m'].is_integer()
  for dev in ['Mpb1','Mpb2','Mpb3','Mpb4']:assert rr[dev]['nodes'][1]==rr[dev]['nodes'][3]
  return s+'dcOpInfo info what=oppoint where=rawfile\n'
def load_design():return json.loads((HERE/'candidate_full/design.json').read_text())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--simulate',action='store_true');ap.add_argument('--output',default='reproduced_full');args=ap.parse_args();t=FrozenTask();d=load_design();hashes={}
 for c in t.corners:
  s=t.deck(d,c);saved=(HERE/'candidate_full'/c['id']/'input.scs').read_text();assert s==saved,c['id'];hashes[c['id']]=hashlib.sha256(s.encode()).hexdigest()
 print(json.dumps({'exact_deck_matches':12,'mos_instances':17,'four_gate_body_ties':True,'sha256':hashes},indent=2),flush=True)
 if args.simulate:
  out=(HERE/args.output).resolve();assert out.is_relative_to(HERE) and not out.exists(),'Use a new output inside this directory'
  result=t.evaluate(d,out,keep_raw=True);cons,counts,ok=aggregate(t.cfg['constraints'],t.corners,result)
  write(out/'design.json',d);write(out/'metrics.json',{'constraints':cons,'diagnostics':result,'corner_summary':counts,'execution_ok':ok,'feasible':ok and all(c['passed'] for c in cons.values()),'design':d,'interpretation':'gain200'})
  print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
