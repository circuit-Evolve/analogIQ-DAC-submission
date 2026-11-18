"""One-time source freeze/config generator; reads original, writes gm_c-owned files only."""
from pathlib import Path
import json, shutil, hashlib
P=Path(__file__).resolve().parent
S=Path('<WORK>/four-papers-20261107/gm_c')
T=P/'templates/gm_c'
files=['assumptions.json','comparison.json','metrics.json','source_sizing.csv','derived_cap.json','design_inventory.json']
for f in files: shutil.copy2(S/f,T/f)
shutil.copy2(S/'sim/cores.scs',T/'cores.scs')
jobs=['OTA_DIFF','OTA_CM','FILTER_AC_NOISE','OTA_LITERAL','IP3_TWO_TONE','FILTER_TRANSIENT']+[f'P1DB_{i}' for i in range(14)]
for name in jobs: shutil.copy2(S/'sim'/name/'input.scs',T/(name+'.scs'))
groups={
 'input_p':['M1','M3'],'input_n':['M2','M4'],
 'cross_n':['M5','M9'],'cross_p':['M6','M10'],
 'load_n':['M7','M11'],'load_p':['M8','M12'],
 'cm_out_n':['M13','M15'],'cm_out_p':['M14','M16'],
 'cm_node_n':['M17','M19','M23','M26R','M28R'],
 'cm_node_p':['M18','M20','M24','M25R','M27R'],
 'cm_fb_n':['M21'],'cm_fb_p':['M22'],
 'bias_n':['M25','M26'],'bias_p':['M27','M28']}
variables=[]
for group,devs in groups.items():
    w,l=((.13e-6,.2e-6) if group in ['cross_n','load_n'] else (.365e-6,.1e-6) if group in ['cross_p','load_p'] else (.6e-6,.12e-6) if group.endswith('_n') else (1.18e-6,.1e-6))
    for parameter,initial in [('w',w),('l',l)]:
        lo=max(.12e-6,initial/5) if parameter=='w' else .1e-6
        hi=initial*10 if parameter=='w' else 1e-6
        variables.append(dict(name=group+'_'+parameter,kind='real',unit='m',lower=lo,upper=hi,initial=initial,scale='log',binding=dict(instances=devs,parameter=parameter,cell='ota_fig2_interpreted',mirror_cell='ota_fig2_literal'),provenance='Table 1 exact initial; shared across all four OTA cores; literal diagnostic mirrors geometry'))
for name,devs in [('cap_b_F',['C1','C2']),('cap_d_F',['C3','C4'])]:
    variables.append(dict(name=name,kind='real',unit='F',lower=1e-13,upper=1e-8,initial=7.65804778642e-12,scale='log',binding=dict(instances=devs,parameter='c',cell='filter_fig3_reconstruction'),provenance='Inferred once from baseline gm/(2*pi*15MHz); exact frozen simulator value (12 significant digits); not re-derived after mutations'))
variables.append(dict(name='vt_bias_V',kind='real',unit='V',lower=.1,upper=.9,initial=.5,scale='linear',binding=dict(instances=['VT_SRC'],parameter='dc',cell='__top__'),provenance='Existing DUT tuning bias; inferred initial half-supply. VDD/VREF/input common mode and signals remain fixed.'))
metrics=json.loads((S/'comparison.json').read_text())
conds=dict(process='NN',temperature_C=27,VDD_V=1,VREF_V=.5,input_common_mode_V=.5,nominal_only=True)
constraints=[]
for m in metrics:
    if m.get('diagnostic_only'):continue
    bounds=sorted([m['paper_value']*.9,m['paper_value']*1.1])
    constraints.append(dict(name=m['name'],metric=m['name'],recipe=m['test'],lower=bounds[0],upper=bounds[1],paper_value=m['paper_value'],unit=m['unit'],conditions=conds,aggregate='worst',expression=m['expression'],reference=m['reference'],note=m.get('note','')))
cfg=dict(task_id='gm_c',topology_id='gm_c_four_ota_fig3_reconstruction',family='gm_c_filter',technology_id='gpdk090',description='Four physical 32-MOS OTA cores, frozen Fig3 hypothesis with inferred side summing resistors and capacitor seed; nominal paper-start sizing; six comparable scalar bands. No paper-exact topology claim.',variables=variables,constraints=constraints,conditions=conds,objective=None,diagnostics=[m for m in metrics if m.get('diagnostic_only')],profiles={'search_full':jobs[:3],'full':jobs},assumptions=json.loads((S/'assumptions.json').read_text()),source_root=str(S),bounds_provenance='Engineering search bounds, not paper limits: W max(120nm,seed/5)..10*seed; L 100nm..1um; pair capacitance .1pF..10nF; existing VT bias .1.. .9V. All MOS m=1; inferred summing resistors fixed 1kohm.')
cfg['conditions']=[dict(id='NN_27',model_set='NN',temperature_C=27,nominal=True)]
cfg['operating_conditions']=dict(supply_V=1,VREF_V=.5,input_common_mode_V=.5,temperature_C=27)
for c in cfg['constraints']:c['conditions']=['NN_27']
(P/'gm_c.json').write_text(json.dumps(cfg,indent=2)+'\n')
(P/'gm_c_paper_seed.json').write_text(json.dumps({v['name']:v['initial'] for v in variables},indent=2)+'\n')
(T/'provenance.json').write_text(json.dumps({'source_root':str(S),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in T.iterdir() if p.is_file() and p.name!='provenance.json'}},indent=2)+'\n')
