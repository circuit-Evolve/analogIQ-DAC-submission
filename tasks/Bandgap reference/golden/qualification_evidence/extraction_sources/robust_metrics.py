"""Explicit target directions and scalar definitions for the 10 November search."""
import math
import numpy as np

UPPER_ONLY = {'Power_uW', 'TC_19_120_ppm_C', 'Line_sensitivity_percent',
              'MISO_quiescent_power', 'BP_noise_in', 'BP_noise_out', 'HPF_Rail_power_mW'}

def apply_directions(constraints):
    for c in constraints:
        if c['name'] in UPPER_ONLY:
            c['lower'] = 0
            c['target_policy'] = 'User approved: lower is better; original upper tolerance retained'
        elif c['name'] == 'PSRR_LF_dB':
            c['upper'] = None
            c['target_policy'] = 'User approved: higher is better; original lower tolerance retained'

def hpf_scalars(frequency, gain):
    f = np.asarray(frequency); g = np.asarray(gain)
    if (len(f) < 3 or len(f) != len(g) or not np.all(np.isfinite(f)) or
        not np.all(np.isfinite(g)) or np.any(g <= 0) or np.any(np.diff(f) <= 0) or
        f[0] > 1 or f[-1] < 20000):
        raise ValueError('Invalid or insufficient HPF AC response')
    db = 20*np.log10(g)
    sample = lambda x: float(np.interp(np.log10(x), np.log10(f), db))
    ref = sample(math.sqrt(2000*20000))
    pb = np.r_[sample(2000), db[(f>2000)&(f<20000)], sample(20000)]
    band = np.r_[sample(200), db[(f>200)&(f<10000)], sample(10000)]
    return {'HPF_gain_200Hz_dB': sample(200), 'HPF_passband_gain_dB': ref,
            'HPF_gain_500Hz_dB': sample(500),
            'HPF_attenuation_50Hz_dB': ref-sample(50),
            'HPF_passband_ripple_dB': float(np.ptp(pb)),
            'HPF_peaking_dB': float(max(band)-ref)}

def gain_spec(mode):
    names = {'gain200':'HPF_gain_200Hz_dB', 'passband':'HPF_passband_gain_dB'}
    name = names[mode]
    freq = '200' if mode=='gain200' else 'sqrt(2000*20000)'
    return {'name':name, 'metric':name, 'unit':'dB', 'lower':-3.5, 'upper':-2.5,
            'paper_value':-3.06, 'recipe':'DTMOS_HPF_NOMINAL',
            'expression':'value(dB20(getData("VOUT_SENSE:p" ?result "ac-ac")) '+freq+')',
            'source':'Paper Fig6a gain mean -3.06dB; user acceptance -3.5..-2.5dB; frequency is not specified by paper',
            'interpretation':mode+' branch; alternative gain definition tracked, not simultaneously constrained'}

def startup_score(diag):
    if diag.get('status')!='completed': return None
    keys=['tail_mean_V','tail_vpp_V','dc_relative_mismatch']
    if any(not isinstance(diag.get(k),(int,float)) or not math.isfinite(diag[k]) for k in keys):return None
    return max(abs(diag['tail_mean_V']-1.2)/.12, diag['tail_vpp_V']/.001,
               diag['dc_relative_mismatch']/.01)
