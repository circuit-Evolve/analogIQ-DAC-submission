"""Frozen MISO paper-start adapter. No imports or writes into the source project."""
from pathlib import Path
import json, math, re, os, signal, subprocess, time
import numpy as np
from engine import mutate, read_wave, dc

HERE=Path(__file__).resolve().parent
TEMPLATES=HERE/'templates'/'miso'


def crossing(x,y,threshold):
    """First falling crossing, log-frequency interpolation (frozen comparison)."""
    hits=np.flatnonzero((y[:-1]>=threshold)&(y[1:]<threshold))
    if not len(hits): return None
    j=int(hits[0])
    return float(np.exp(np.interp(threshold,[y[j+1],y[j]],[np.log(x[j+1]),np.log(x[j])])))


class Task:
    def __init__(self,profile='search_full'):
        self.profile=profile
        self.cfg=json.loads((HERE/'miso.json').read_text())
        self.variables=self.cfg['variables']
        self.templates={p.stem:p.read_text() for p in sorted(TEMPLATES.glob('*.scs'))}
        self.score_jobs=sorted({c['recipe'] for c in self.cfg['constraints']})

    def paper_design(self):
        return json.loads((HERE/'miso_paper_seed.json').read_text())

    def decks(self,design):
        if set(design)!={v['name'] for v in self.variables}: raise ValueError('MISO sizing keys differ from frozen variables')
        changes={}; top={}
        for v in self.variables:
            value=design[v['name']]
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not v['lower']<=value<=v['upper']:
                raise ValueError('Invalid MISO sizing: '+v['name'])
            # Keep paper seed decks byte-identical; no rounding of derived VCTRL.
            if value==v['initial']: continue
            b=v['binding']
            for dev in b['instances']:
                if b['cell']=='__top__':top.setdefault(dev,{})[b['parameter']]=value
                else:changes.setdefault(b['cell'],{}).setdefault(dev,{})[b['parameter']]=value
        jobs=self.templates if self.profile in ('full','final','diagnostic_full','full_verify') else self.score_jobs
        out={}
        for job in jobs:
            s=self.templates[job]
            active={cell:devs for cell,devs in changes.items() if re.search(r'^subckt '+re.escape(cell)+r' ',s,re.M)}
            if active:s=mutate(s,active)
            for dev,params in top.items():
                for parameter,value in params.items():
                    pattern=r'(?m)^('+re.escape(dev)+r' \([^\n]+\) [^\n]*?\b'+parameter+r'=)\S+'
                    s,n=re.subn(pattern,lambda m:m[1]+format(value,'.17g'),s)
                    if n!=1: raise ValueError('Missing top bias binding '+dev)
            out[job]=s
        return out

    def _ocean(self,paths,diagnostics):
        """Use actual Cadence functions, one isolated batch, never live-session edits."""
        expressions={c['name']:(c['recipe'],c['expression']) for c in self.cfg['constraints'] if c['name'] in ('MISO_BP_frequency','LP_THD','BP_THD')}
        present={name:(job,expr) for name,(job,expr) in expressions.items() if job in paths}
        if not present:return {}
        # Evaluation job directories share an owned parent. Never write to source paths.
        parent=Path(next(iter(paths.values()))).resolve().parent
        import tempfile
        with tempfile.TemporaryDirectory(prefix='miso_ocean_',dir=parent) as temp:
            work=Path(temp);(work/'cds.lib').write_text('# Isolated read-only results extraction.\n')
            lines=[]
            for name,(job,expr) in present.items():
                raw=Path(paths[job]).resolve()/'raw'
                lines += ['openResults('+json.dumps(str(raw))+')','v=errset('+expr+' t)',f'when(v && numberp(car(v)) printf("MISO_SCALAR {name} %.17g\\n" car(v)))']
            lines.append('exit()');script=work/'extract.ocn';script.write_text('\n'.join(lines)+'\n')
            start=time.monotonic()
            with (work/'stdout.log').open('w') as f:
                p=subprocess.Popen(['/opt/cadence/bin/virtuoso','-nograph','-nocdsinit','-cdslib',str(work/'cds.lib'),'-restore',str(script),'-log',str(work/'virtuoso.log')],cwd=work,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
                try:rc=p.wait(timeout=90)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGTERM)
                    try:p.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                    rc=124
            text=(work/'stdout.log').read_text(errors='replace')
            if (work/'virtuoso.log').exists():text+='\n'+(work/'virtuoso.log').read_text(errors='replace')
            diagnostics['ocean']={'returncode':rc,'runtime_seconds':time.monotonic()-start,'method':'Cadence deriv/cross and thd builtin, 8192 samples, fixed saved windows','interpolation_warning': 'interpolated' in text,'log':text[-16000:]}
            return {name:float(value) for name,value in re.findall(r'MISO_SCALAR (\w+) ([-+0-9.eE]+)',text)} if rc==0 else {}

    def extract(self,paths):
        paths={k:Path(v) for k,v in paths.items()}
        values={c['metric']:None for c in self.cfg['constraints']};diagnostics={'errors':{}}
        def wave(job,filename,signals):return read_wave(paths[job]/'raw'/filename,signals)
        def assign(name,fn):
            try:
                val=fn()
                if val is not None and math.isfinite(float(val)):values[name]=float(val)
            except Exception as exc:diagnostics['errors'][name]=str(exc)
        for k in ('Y1','Y2','IZP'):
            job='CORE_'+k;sig='ZP_SRC:p' if k=='IZP' else 'X'
            try:
                x,y=wave(job,'ac.ac',[sig]); a=np.abs(y[sig]);values[k+'_gain']=float(a[0]); bw=crossing(x,a,a[0]/np.sqrt(2))
                # Fine sweep is existing characterization, but a new design can move
                # its first crossing outside that window. Never choose a later crossing.
                if k=='IZP' and bw is not None:
                    xf,yf=wave(job,'ac_fine.ac',[sig]);af=np.abs(yf[sig]);threshold=a[0]/np.sqrt(2)
                    fine=crossing(xf,af,threshold)
                    if xf[0]<=bw<=xf[-1] and fine is not None and af[0]>=threshold:bw=fine
                values[k+'_bandwidth']=bw
            except Exception as exc:diagnostics['errors'][k]=str(exc)
        for k,port in [('RX','X'),('RZP','ZP'),('ROP','OP'),('ROM','OM')]:
            def resistance(k=k,port=port):
                sig=port if k=='RX' else port+'_SRC:p';z=wave('CORE_'+k,'ac.ac',[sig])[1][sig][0]
                return np.real(z if k=='RX' else -1/z)
            assign(k,resistance)
        assign('OTA_gm',lambda:abs(wave('CORE_GM','ac.ac',['OM_SRC:p'])[1]['OM_SRC:p'][0]))
        def power():
            d=dc(paths['VM_LP']/'raw'/'dcOp.dc');return .9*(-d['VDD_SRC:p']+d['VSS_SRC:p'])
        assign('MISO_quiescent_power',power)
        for sig in ('in','out'):
            def noise(sig=sig):
                x,y=wave('VM_BP','noise.noise',[sig]);return np.interp(3.98e6,x,y[sig])
            assign('BP_noise_'+sig,noise)
        try:
            for name,value in self._ocean(paths,diagnostics).items():
                if name in values and math.isfinite(value):values[name]=value
        except Exception as exc:diagnostics['errors']['ocean']=str(exc)
        # Retain available simultaneous filter responses as unscored diagnostics.
        diagnostics['responses']={}
        for job in sorted(paths):
            if not job.startswith(('VM_','CM_')) or job.endswith('_TRAN'):continue
            try:
                x,y=wave(job,'ac.ac',['VOUT','IOUT_SRC:p']);diagnostics['responses'][job]={}
                for sig,a in y.items():
                    a=np.abs(a);diagnostics['responses'][job][sig]={'gain_at_1Hz':float(a[0]),'gain_at_3p98MHz':float(np.interp(3.98e6,x,a)),'peak_gain':float(a.max())}
            except Exception as exc:diagnostics['errors'][job+'_diagnostics']=str(exc)
        return values,diagnostics

    def plan_text(self):
        annotations=['MISO variable bindings (SI; only these DUT dimensions/passives/biases may vary):']
        for v in self.variables:annotations.append(f"// {v['name']}: {v['binding']}; seed={v['initial']:.17g}; bounds=[{v['lower']:.17g}, {v['upper']:.17g}]")
        s=self.templates['VM_BP'];body=s[s.index('subckt mdvccta_fig2'):s.index('// Library name: DAC_20261107_MISO\n// Cell name: VM_BP_tb')]
        for v in self.variables:
            b=v['binding']
            if b['cell']=='__top__':
                for dev in b['instances']:
                    line=re.search(r'(?m)^'+re.escape(dev)+r' [^\n]+',s)[0]
                    body+='\n'+re.sub(r'\bdc=\S+','dc=<'+v['name']+'>',line)
                continue
            m=re.search(r'(?m)^subckt '+b['cell']+r' .*?\n(.*?)^ends '+b['cell'],body,re.S)
            part=m[1]
            for dev in b['instances']:
                pattern=r'(?m)^(\s*'+re.escape(dev)+r' \([^\n]+\) [^\n]*?\b'+b['parameter']+r'=)\S+'
                part=re.sub(pattern,lambda match:match[1]+'<'+v['name']+'>',part)
            body=body[:m.start(1)]+part+body[m.end(1):]
        return '\n'.join(annotations)+'\n'+body
