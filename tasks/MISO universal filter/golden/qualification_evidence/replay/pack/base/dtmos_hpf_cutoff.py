"""Measured-passband HPF cutoff; never substitute a falling LPF crossing."""
import numpy as np

PB_START=2000.0
PB_STOP=20000.0
PB_REF=(PB_START*PB_STOP)**0.5
FLATNESS_DB=1.0
HALF_POWER_DB=20*np.log10(np.sqrt(2))
NOTE=('First rising half-power crossing relative to measured passband gain. '
      'Provisional passband qualification window: 2-20 kHz (10-100 times the '
      '200 Hz target), at most 1 dB peak-to-peak variation; reference gain at '
      'the geometric centre, 6.3246 kHz. The low-frequency gain must be below '
      'the half-power level. Window and flatness are measurement assumptions, '
      'not paper specifications; a failed qualification produces no fc. '
      'Target band: 180-220 Hz.')
EXPRESSION=('let((g p ref threshold) '
 'g=dB20(getData("VOUT_SENSE:p" ?result "ac-ac")) '
 'p=clip(g 2000 20000) '
 'ref=value(g sqrt(2000*20000)) '
 'threshold=ref-20*log10(sqrt(2)) '
 'if(((ymax(p)-ymin(p))<=1) && (value(g 1)<threshold) '
 'then cross(clip(g 1 2000) threshold 1 "rising") else nil))')

def measure(frequency,gain):
    f=np.asarray(frequency);db=20*np.log10(np.asarray(gain))
    sample=lambda x:float(np.interp(np.log10(x),np.log10(f),db))
    p=np.r_[sample(PB_START),db[(f>PB_START)&(f<PB_STOP)],sample(PB_STOP)]
    ref=sample(PB_REF);threshold=ref-HALF_POWER_DB
    result={'passband_window_Hz':[PB_START,PB_STOP],
            'passband_reference_dB':ref,'passband_span_dB':float(np.ptp(p)),
            'half_power_threshold_dB':threshold,'cutoff_Hz':None}
    if f[0]>1 or f[-1]<PB_STOP:
        result['status']='FAIL_INSUFFICIENT_AC_RANGE';return result
    if np.ptp(p)>FLATNESS_DB:
        result['status']='FAIL_NO_FLAT_HPF_PASSBAND';return result
    if sample(1)>=threshold:
        result['status']='FAIL_NO_LOW_FREQUENCY_REJECTION';return result
    ix=np.where((db[:-1]<threshold)&(db[1:]>=threshold)&(f[1:]<=PB_START))[0]
    if not len(ix):
        result['status']='FAIL_NO_RISING_CROSSING';return result
    i=ix[0];fc=float(np.exp(np.interp(threshold,db[i:i+2],np.log(f[i:i+2]))))
    result.update(cutoff_Hz=fc,status='PASS' if 180<=fc<=220 else 'FAIL_TARGET')
    return result
