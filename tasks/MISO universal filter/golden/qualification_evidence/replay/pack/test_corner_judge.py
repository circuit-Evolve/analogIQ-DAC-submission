from corner_judge import aggregate
s=[{'name':'gain','lower':9,'upper':11,'paper_value':10}];c=[{'id':'TT'},{'id':'FF'}]
def run(rows):return aggregate(s,c,{'corners':rows,'execution_ok':True})
def row(k,v,ok=True):return {'id':k,'values':{'gain':v},'execution_ok':ok}
x,n,ok=run([row('TT',10),row('FF',13)]);assert not x['gain']['passed'] and x['gain']['value']==13 and n['all_metrics_pass_corners']==1 and ok
x,n,ok=run([row('TT',10)]);assert not x['gain']['passed'] and x['gain']['value'] is None and not ok
x,n,ok=run([row('TT',10),row('FF',10,False)]);assert not x['gain']['passed'] and not ok
x,n,ok=run([row('TT',10),row('FF',float('nan'))]);assert x['gain']['value'] is None and n['missing_scalars']==1
x,n,ok=run([row('TT',10),row('FF',10)]);assert x['gain']['passed'] and n['all_metrics_pass_corners']==2 and ok
s[0].update(lower=-26.4,upper=-21.6,paper_value=-24);x,n,ok=run([row('TT',-24),row('FF',-30)]);assert x['gain']['value']==-30 and not x['gain']['passed']
s[0].update(lower=0,upper=6,paper_value=6,upper_exclusive=True);x,n,ok=run([row('TT',1),row('FF',6)]);assert not x['gain']['passed']
print('PASS: adverse, missing, failed, nonfinite, passing, negative-dB and strict-bound corners')
