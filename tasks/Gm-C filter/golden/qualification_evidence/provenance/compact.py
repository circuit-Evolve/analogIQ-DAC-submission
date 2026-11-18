import re
import reconstruct as r

class CompactTask(r.Task):
 def corner_decks(self,d,c):
  decks=super().corner_decks(d,c)
  for job,deck in decks.items():
   deck=re.sub(r'(?m)^saveOptions .*$', 'saveOptions options save=selected currents=selected\nsave VOP VOM VIP VIM DUT.AP DUT.AM DUT.BP DUT.BM DUT.DP DUT.DM',deck)
   deck=re.sub(r'(?m)^(noise .*iprobe=VINP)$',r'\1 save=selected',deck)
   decks[job]=deck
  return decks
