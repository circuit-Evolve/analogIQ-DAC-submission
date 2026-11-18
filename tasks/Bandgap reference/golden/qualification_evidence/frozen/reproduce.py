"""Recreate every bandgap deck exactly; --simulate adds fresh full15 verification."""
from golden_task import *
import argparse,re,hashlib

def topology(s):
 b=re.search(r'(?ms)^subckt bgr_fig3_paper .*?^ends bgr_fig3_paper',s)[0]
 return re.findall(r'^\s*(\S+)\s+\(([^)]+)\)\s+(\S+)',b,re.M)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--simulate',action='store_true');ap.add_argument('--output',default='reproduced_full');args=ap.parse_args()
 t=GoldenTask();d=design();decks=t.decks(d);reference=topology(t.templates['nominal']);hashes={}
 for c in t.conditions:
  for analysis in ['nominal','temperature','startup']:
   s=t.corner_deck(decks['nominal' if analysis=='startup' else analysis],c['model_set'],c['supply_V'])
   if analysis=='startup':s=t._startup_deck(s)
   assert topology(s)==reference
   p=HERE/'ratio_binned_candidate_full'/c['id']/analysis/'input.scs';assert s==p.read_text(),str(p)
   hashes[str(p.relative_to(HERE))]=hashlib.sha256(s.encode()).hexdigest()
 for process in ['tt','ff','ss','sf','fs']:
  s=t.corner_deck(decks['line'],process,1.8);p=HERE/'ratio_binned_candidate_full'/(process.upper()+'_line')/'input.scs';assert s==p.read_text();hashes[str(p.relative_to(HERE))]=hashlib.sha256(s.encode()).hexdigest()
 result={'exact_decks':len(hashes),'original_connectivity_preserved':True,'MOS_instances':sum(k[0].startswith('M') for k in reference),'sha256':hashes};write(HERE/'reproduction_check.json',result);print(json.dumps({k:v for k,v in result.items() if k!='sha256'}),flush=True)
 if args.simulate:
  out=(HERE/args.output).resolve();assert out.is_relative_to(HERE) and not out.exists()
  result=verify(t,out,d);print(json.dumps(result['corner_summary']),flush=True)
if __name__=='__main__':main()
