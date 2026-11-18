"""Fresh 500-point/decade replay of a frozen search candidate."""
import sys,json,re
from pathlib import Path
N=Path(__file__).resolve().parent
sys.path[:0]=[str(N.parent),str(N.parent/'continuation_20261113')]
import reconstruct as r
from run_policy import apply
apply(r.work)
from feedback_task import FeedbackTask
class DenseTask(FeedbackTask):
 def corner_decks(self,*a,**kw):
  return {k:re.sub(r'\bdec=100\b','dec=500',v) for k,v in super().corner_decks(*a,**kw).items()}
r.TASK=DenseTask()
source=Path(sys.argv[1]);candidate=json.loads(source.read_text());design=candidate.get('design',candidate)
e=r.run(sys.argv[2],design,full=True)
r.work.dump(N/(sys.argv[2]+'.json'),e)
print(json.dumps({'label':e['label'],'grade':e['grade'],'shapes':[x['diagnostics']['filter_response']['strict_shape_screen'] for x in e['corners']]},indent=2))
