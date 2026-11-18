"""Frozen nominal gm-C task. No import or writes to original circuit project."""
from pathlib import Path
import json
import math
import re
import numpy as np
from engine import mutate, read_wave

HERE=Path(__file__).resolve().parent
TEMPLATE=HERE/'templates/gm_c'

def validate_wave(x,y):
    if len(x)<2 or len(x)!=len(y) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or np.any(x<=0) or np.any(np.diff(x)<=0):
        raise ValueError('Missing, invalid or nonmonotonic waveform')

def crossing(x,y,target):
    validate_wave(x,y)
    if not math.isfinite(float(target)) or target<=0: raise ValueError('Invalid crossing threshold')
    ids=np.where((y[:-1]>=target)&(y[1:]<target))[0]
    if len(ids)==0:return None
    j=ids[0]
    return float(np.exp(np.interp(target,[y[j+1],y[j]],[np.log(x[j+1]),np.log(x[j])])))

class Task:
    def __init__(self,profile='search_full'):
        self.cfg=json.loads((HERE/'gm_c.json').read_text())
        self.variables=self.cfg['variables']
        if profile in ('full_verify','verification','final'):profile='full'
        if profile not in self.cfg['profiles']:raise ValueError('Unknown gm_c profile: '+str(profile))
        self.profile=profile
        self.core=(TEMPLATE/'cores.scs').read_text()

    def paper_design(self):
        return json.loads((HERE/'gm_c_paper_seed.json').read_text())

    def decks(self,design):
        expected={v['name'] for v in self.variables}
        if set(design)!=expected:raise ValueError('Sizing keys differ: '+str(set(design)^expected))
        for v in self.variables:
            x=design[v['name']]
            if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not v['lower']<=x<=v['upper']:
                raise ValueError('Invalid sizing: '+v['name'])
        changes={}
        for v in self.variables:
            value=design[v['name']]
            if value==v['initial']:continue  # seed remains exact frozen text, including SI formatting
            b=v['binding']
            if b['cell']=='__top__':continue
            for cell in [b['cell']]+([b['mirror_cell']] if 'mirror_cell' in b else []):
                for instance in b['instances']:
                    changes.setdefault(cell,{}).setdefault(instance,{})[b['parameter']]=value
        core=mutate(self.core,changes)
        decks={}
        for job in self.cfg['profiles'][self.profile]:
            deck=(TEMPLATE/(job+'.scs')).read_text()
            deck,n=re.subn(r'(?m)^include "[^\n]+/gm_c/sim/cores\.scs"$',lambda _:core,deck)
            if n!=1:raise ValueError('Frozen core include not found')
            if design['vt_bias_V']!=.5:
                deck,n=re.subn(r'(?m)^VT_SRC \(VT 0\) vsource dc=\.5$',f"VT_SRC (VT 0) vsource dc={design['vt_bias_V']:.12g}",deck)
                if n!=1:raise ValueError('VT binding absent')
            decks[job]=deck
        return decks

    def plan_text(self):
        annotations=['// gm-C fixed Fig3 hypothesis; all four OTA instances share the interpreted core.']
        for v in self.variables:
            b=v['binding']
            annotations.append(f"// {v['name']} -> {b['cell']}/"+','.join(b['instances'])+f".{b['parameter']}; initial={v['initial']} {v['unit']}; bounds=[{v['lower']},{v['upper']}]")
        core=self.core
        for v in self.variables:
            b=v['binding']
            if b['cell']=='__top__':continue
            for cell in [b['cell']]+([b['mirror_cell']] if 'mirror_cell' in b else []):
                block=re.search(r'(?m)^subckt '+re.escape(cell)+r' .*?\n(.*?)^ends '+re.escape(cell),core,re.S)
                body=block[1]
                for instance in b['instances']:
                    pattern=r'(?m)^'+re.escape(instance)+r' \([^\n]+\) [^\n]+'
                    body=re.sub(pattern,lambda m:re.sub(r'\b'+b['parameter']+r'=\S+',b['parameter']+'=<'+v['name']+'>',m[0]),body)
                core=core[:block.start(1)]+body+core[block.end(1):]
        return '\n'.join(annotations)+'\n'+core+'\n// Existing DUT tuning-bias source:\nVT_SRC (VT 0) vsource dc=<vt_bias_V>\n'

    def extract(self,paths):
        values={c['metric']:None for c in self.cfg['constraints']}
        diag={'errors':{},'profile':self.profile,'nominal_only':True,'paper_exact_reproduction':False,'nonlinear':{m['name']:{'value':None,'diagnostic_only':True,'status':'NOT_COMPARABLE_MISSING_PAPER_CONDITIONS'} for m in self.cfg['diagnostics']}}
        def path(job,name):
            if job not in paths:raise ValueError('Successful output missing: '+job)
            p=Path(paths[job])
            return (p if p.name=='raw' else p/'raw')/name
        def ac(job):
            f,v=read_wave(path(job,'ac.ac'),{'VOP','VOM'})
            h=v['VOP']-v['VOM'];validate_wave(f,h)
            if not np.isclose(f[0],1,rtol=1e-10,atol=0):raise ValueError('Missing 1Hz scalar point')
            return f,v,h
        def attempt(job,fn):
            try:fn()
            except (OSError,ValueError,KeyError,IndexError,TypeError,ZeroDivisionError,FloatingPointError) as e:diag['errors'][job]=str(e)
        def diff():
            f,v,h=ac('OTA_DIFF')
            if abs(h[0])<=0:raise ValueError('Zero differential gain')
            values['OTA_differential_gain_dB']=float(20*np.log10(abs(h[0])))
            ugf=crossing(f,abs(h),1)
            values['OTA_unity_gain_frequency_Hz']=ugf
            if ugf is not None:
                ph=np.unwrap(np.angle(h))*180/np.pi
                values['OTA_phase_margin_deg']=float(180+np.interp(np.log(ugf),np.log(f),ph))
            else:diag['errors']['OTA_DIFF_crossing']='No falling unity crossing; UGF and phase margin invalid'
        def cm():
            f,v,h=ac('OTA_CM');gain=abs((v['VOP'][0]+v['VOM'][0])/2)
            if gain<=0:raise ValueError('Zero common-mode gain')
            values['OTA_common_mode_gain_dB']=float(20*np.log10(gain))
        def filt():
            f,v,h=ac('FILTER_AC_NOISE')
            cutoff=crossing(f,abs(h),abs(h[0])/np.sqrt(2))
            values['Filter_cutoff_Hz']=cutoff
            if cutoff is None:diag['errors']['FILTER_cutoff']='No falling relative -3dB crossing'
            diag['filter_dc_gain_dB']=float(20*np.log10(abs(h[0])))
            diag['filter_peak_gain_dB']=float(20*np.log10(max(abs(h))))
            diag['filter_peaking_above_dc_dB']=float(20*np.log10(max(abs(h))/abs(h[0])))
            fn,vn=read_wave(path('FILTER_AC_NOISE','noise.noise'),{'out'});validate_wave(fn,vn['out'])
            if not fn[0]<=1e6<=fn[-1] or not f[0]<=1e6<=f[-1] or np.any(vn['out']<0):raise ValueError('Invalid noise frequency coverage or values')
            gain=np.interp(np.log(1e6),np.log(f),abs(h))
            if gain<=0:raise ValueError('Zero normalization gain')
            values['Filter_input_noise_nV_sqrtHz']=float(1e9*np.interp(np.log(1e6),np.log(fn),vn['out'])/gain)
        attempt('OTA_DIFF',diff);attempt('OTA_CM',cm);attempt('FILTER_AC_NOISE',filt)
        if self.profile=='full':
            def tran(job):
                x,v=read_wave(path(job,'tran.tran.tran'),{'VOP','VOM'})
                selected=x>=20e-6;x=x[selected];out=(v['VOP']-v['VOM'])[selected]
                validate_wave(x,out)
                if x[0]>20.01e-6 or x[-1]<29.99e-6:raise ValueError('Incomplete final 10us Fourier window')
                def a(f):return float(abs(2*np.trapz((out-np.mean(out))*np.exp(-2j*np.pi*f*x),x)/(x[-1]-x[0])))
                return dict(fundamental_V=a(1e6),IM3_V=a(.9e6),output_min_V=float(min(out)),output_max_V=float(max(out)))
            def p1db():
                aa=np.geomspace(.001,.3,14)
                rows=[tran('P1DB_'+str(i)) for i in range(14)]
                gg=np.array([r['fundamental_V']/a for r,a in zip(rows,aa)])
                if np.any(gg<=0):raise ValueError('Invalid compression gain')
                drop=20*np.log10(gg[0]/gg);idx=np.where(drop>=1)[0]
                if not len(idx):raise ValueError('No 1dB compression crossing in fixed amplitude range')
                j=idx[0]
                amp=np.exp(np.interp(1,drop[j-1:j+1],np.log(aa[j-1:j+1])))
                diag['nonlinear']['OTA_input_P1dB_dBm']['value']=float(10*np.log10(amp**2/(2*50*1e-3)))
                diag['compression_characterization']=rows
            def ip3():
                two=tran('IP3_TWO_TONE')
                if two['fundamental_V']<=0 or two['IM3_V']<=0:raise ValueError('Invalid IP3 spectrum')
                diag['nonlinear']['OTA_IIP3_dBm']['value']=float(-50+10*np.log10(two['fundamental_V']/two['IM3_V']))
                diag['IP3_TWO_TONE']=two
            def filter_transient():diag['FILTER_TRANSIENT']=tran('FILTER_TRANSIENT')
            def literal():
                f,v,h=ac('OTA_LITERAL');diag['literal_gain_dB']=float(20*np.log10(abs(h[0])))
            attempt('P1DB',p1db);attempt('IP3_TWO_TONE',ip3);attempt('FILTER_TRANSIENT',filter_transient);attempt('OTA_LITERAL',literal)
        for key,value in values.items():
            if value is not None and not math.isfinite(value):values[key]=None;diag['errors'][key]='Nonfinite scalar'
        return values,diag
