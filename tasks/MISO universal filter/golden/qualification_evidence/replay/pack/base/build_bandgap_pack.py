from pathlib import Path
import json,re,shutil,hashlib
P=Path(__file__).resolve().parent;S=Path('<WORK>/four-papers-20261107/bandgap');T=P/'templates/bandgap';T.mkdir(parents=True,exist_ok=True)
s=(S/'ocean_verify/native_nominal/input.scs').read_text();(T/'nominal.scs').write_text(s)
base='\n'.join(l for l in s.splitlines() if not l.startswith(('tran tran','finalTimeOP ','ac ac','dcOp dc')))+'\n'
(T/'temperature.scs').write_text(base+'dc dc param=temp start=-40 stop=120 step=1\n')
(T/'line.scs').write_text(base+'dc dc param=VS start=1.71 stop=1.89 step=.002\n')
groups=[('PMIRROR',['M1','M2','M3'],3.19,.4),('NPTAT',['M4']+['M5_'+str(i) for i in range(1,11)],75.13,.4),('PBIAS',['M6','M7'],5,.55),('PGAIN',['M8'],84.77,2.5),('NGAIN',['M9'],28,2.5),('PINPUT',['M10','M11'],6.4,1.2),('NLOAD',['M12','M13'],1.3,1)]
vs=[]
for tag,names,w,l in groups:
 for param,val,lo,hi in [('w',w,.42,300),('l',l,.15,10)]:
  vs.append(dict(name=tag+'_'+param,kind='real',unit='m',lower=lo*1e-6,upper=hi*1e-6,initial=val*1e-6,scale='log',binding=dict(instances=['bgr_fig3_paper.'+n for n in names],parameter=param),cell='bgr_fig3_paper',devices=names,parameter=param))
for name,param,val,lo,hi,unit in [('R1','r',30000,1000,1e6,'ohm'),('R2','r',83600,1000,1e6,'ohm'),('R3','r',118300,1000,2e6,'ohm'),('R4','r',100000,10000,2e6,'ohm'),('CC','c',1e-12,1e-14,1e-10,'F')]:
 vs.append(dict(name=name+'_'+param,kind='real',unit=unit,lower=lo,upper=hi,initial=val,scale='log',binding=dict(instances=['bgr_fig3_paper.'+name],parameter=param),cell='bgr_fig3_paper',devices=[name],parameter=param))
rows=json.loads((S/'comparison.json').read_text())['comparison'];cons=[]
for row in rows:
 p=row['paper_value'];cons.append(dict(name=row['metric'],metric=row['metric'],recipe='retained_paper_nominal',lower=p-.1*abs(p),upper=p+.1*abs(p),paper_value=p,conditions=['TT_27'],aggregate='worst',expression=row['expression'],source=row['source']))
cfg=dict(task_id='bandgap',topology_id='bgr_fig3_paper',family='bandgap_reference',technology_id='sky130',description='Original published sizing, disclosed R4/CC assumptions, TT27C1.8V with retained line/temperature characterization. No process corners added.',variables=vs,constraints=cons,conditions=[dict(id='TT_27',model_set='tt',temperature_C=27,nominal=True)],operating_conditions=dict(supply_V=1.8,line_sweep_min_V=1.71,line_sweep_max_V=1.89,temperature_sweep_min_C=-40,temperature_sweep_max_C=120,TC_interval_min_C=19,TC_interval_max_C=120),objective=None)
(P/'bandgap.json').write_text(json.dumps(cfg,indent=2));(P/'bandgap_paper_seed.json').write_text(json.dumps(dict(parameters={v['name']:v['initial'] for v in vs},source=str(S/'sizing.json'),assumptions=json.loads((S/'comparison.json').read_text())['assumptions'],preserved_ratios='M4:M5 total width 1:10; mirrored/input pairs tied'),indent=2));shutil.copy2(S/'comparison.json',P/'bandgap_saved_comparison.json');(P/'bandgap_provenance.json').write_text(json.dumps(dict(source=str(S),sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'sizing.json',S/'comparison.json',S/'ocean_verify/native_nominal/input.scs']},model_geometry_units='Sky130 netlist w/l,area,perimeter are micron-native; no SI reinterpretation.',paper_start=True),indent=2));print('Bandgap:',len(vs),'variables,',len(cons),'targets')
