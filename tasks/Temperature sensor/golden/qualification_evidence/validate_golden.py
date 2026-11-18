from pathlib import Path
import json,re,sys,shutil,hashlib,csv
import numpy as np
G=Path(__file__).parent;R=G.parent.parent;N=G/'native_candidate';S=Path('<WORK>/four_papers_20261109/temperature_sensor/golden_20261110');sys.path.insert(0,str(R));from engine import clean,execute,read_wave
src=S/'native_netlist/temperature_sensor_tb/spectre/schematic/netlist/input.scs';base=clean(src.read_text());shutil.copy2(src,N/'native_input.scs')
def devices(s):
 out={}
 for cell,body in re.findall(r'^subckt (\w+) .*?\n(.*?)^ends \w+',s,re.M|re.S):
  for name,nodes,model,params in re.findall(r'^\s*([MQ]\w+) \(([^\n]+)\) (\S+) ([^\n]+)',body,re.M):out[cell+'/'+name]={'nodes':nodes,'model':model,'params':dict(re.findall(r'\b(w|l|nf|mult|as|ad|ps|pd)=(\S+)',params))}
 return out
ref=devices(clean((G.parent/'sizing/native_candidate/native_input.scs').read_text()));now=devices(base);assert ref.keys()==now.keys() and len(now)==40
for k in now:
 assert now[k]['nodes']==ref[k]['nodes'] and now[k]['model']==ref[k]['model'],k
 for p,v in now[k]['params'].items():assert np.isclose(float(v),float(ref[k]['params'][p]),rtol=1e-10,atol=1e-12),(k,p)
assert json.loads((N/'corners.json').read_text())['process']==['tt','fs','sf']
targets=json.loads((G.parent/'paper_targets.json').read_text())['corners'];out={'native_devices_checked':len(now),'exact_retained_sizing_and_topology':True,'active_corners':['TT','FS','SF'],'power_not_a_paper_target':True,'corners':{},'comparison':[]}
for c in ['tt','fs','sf']:
 d=S/'runs'/c;s=base.replace('section=tt','section='+c);assert execute(s,d,timeout=60)==0
 _,v=read_wave(d/'raw/dc.dc');t=v['temp'];y=v['V_TEMP'];assert len(y)==101 and np.max(np.diff(y))<0
 old=np.loadtxt(G/'verified'/c/'curve.csv',delimiter=',',skiprows=1)[:,1];delta=float(max(abs(y-old)));assert delta<1e-6
 span=float(np.ptp(y));m={'Vout_0C_V':float(y[0]),'Vout_27C_V':float(y[27]),'Vout_100C_V':float(y[-1]),'Sensitivity_mV_C':float(10*(y[-1]-y[0])),'Output_span_mV':1000*span,'Endpoint_linearity_percent_FS':float(100*np.max(abs(y-(y[0]+(y[-1]-y[0])*t/100)))/span)}
 out['corners'][c]={'metrics':m,'returncode':0,'max_difference_from_retained_V':delta,'monotonic':True}
 for k,val in m.items():
  target=targets[c.upper()]['metrics'][k];passed=val<=target*1.1 if k=='Endpoint_linearity_percent_FS' else abs(val/target-1)<=.1
  out['comparison'].append({'corner':c.upper(),'metric':k,'paper_graph_reference':target,'candidate':val,'passed':bool(passed),'rule':'upper bound' if k=='Endpoint_linearity_percent_FS' else '+/-10%'})
 e=G/'fresh_verification'/c;e.mkdir(parents=True,exist_ok=True)
 for f in ['input.scs','status.json','spectre.log']:shutil.copy2(d/f,e/f)
 np.savetxt(e/'curve.csv',np.c_[t,y],delimiter=',',header='temperature_C,Vout_V',comments='')
assert all(r['passed'] for r in out['comparison']);out['two_sided_passes']=15;out['linearity_upper_bound_passes']=3
(G/'verification.json').write_text(json.dumps(out,indent=2))
q=json.dumps
ocn=[f'ss=maeLoadSetup("DAC_20261110_TEMP_GOLDEN" "temperature_sensor_paper_setup" "maestro")','printf("GOLDEN_REOPEN %L\\n" maeGetSetup(?session ss))']
expr=(N/'native/verify_expressions.ocn').read_text();ocn.append(expr);(N/'native/reopen_and_verify.ocn').write_text('\n'.join(ocn))
print(json.dumps({'native_devices':40,'active_corners':out['active_corners'],'two_sided_passes':15,'linearity_upper_bound_passes':3}))
