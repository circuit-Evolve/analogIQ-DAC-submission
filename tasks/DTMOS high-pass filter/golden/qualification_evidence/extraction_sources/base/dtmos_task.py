"""Frozen paper-start DTMOS sizing; no writes or original imports at import time."""
from pathlib import Path
import json
import math
import re
import numpy as np
import engine
from dtmos_hpf_cutoff import measure, NOTE, EXPRESSION

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / 'templates/dtmos'
CELLS = {'CORE': 'dtmos_fig1b_paper', 'HPF': 'dtmos_hpf_derived'}
# Total width; fixed M3 multiplier is applied only at the deck binding.
GROUPS = [
    ('M1', ['M1'], 3, 2),
    ('M24', ['M2', 'M4'], 5, 2),
    ('M3', ['M3'], 150, 2),
    ('Mpb14', ['Mpb1', 'Mpb2', 'Mpb3', 'Mpb4'], 10, 2),
    ('Mpb56', ['Mpb5', 'Mpb6', 'Mpb6_FB'], 40, .5),
    ('Mpb78', ['Mpb7', 'Mpb8', 'Mpb8_FB'], 8, 2),
    ('Mnb12', ['Mnb1', 'Mnb2'], 10, .5),
    ('Mnb3', ['Mnb3'], 10, .5),
    ('Mnb4', ['Mnb4'], 3, 2),
    ('Mnb5', ['Mnb5', 'Mnb5_FB'], 10, .2),
]


class Task:
    def __init__(self, profile='search_full'):
        self.profile = profile
        self.cfg = json.loads((ROOT / 'dtmos.json').read_text())
        self.variables = self.cfg['variables']
        self.templates = {k: (TEMPLATES / (k + '.scs')).read_text() for k in CELLS}

    def paper_design(self):
        return {v['name']: v['initial'] for v in self.variables}

    def decks(self, design):
        if set(design) != {v['name'] for v in self.variables}:
            raise ValueError('DTMOS design must contain exactly all sizing variables')
        for v in self.variables:
            x = design[v['name']]
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not v['lower'] <= x <= v['upper']:
                raise ValueError('Invalid DTMOS sizing: ' + v['name'])
        result = {}
        for kind, cell in CELLS.items():
            changes = {}
            for v in self.variables:
                x = design[v['name']]
                if x == v['initial']:
                    continue
                for dev in v['binding']['instances']:
                    if kind == 'CORE' and dev.endswith('_FB'):
                        continue
                    value = x / 2 if dev == 'M3' and v['binding']['parameter'] == 'w' else x
                    changes.setdefault(dev, {})[v['binding']['parameter']] = value
            result['DTMOS_' + kind + '_NOMINAL'] = engine.mutate(self.templates[kind], {cell: changes}) if changes else self.templates[kind]
        return result

    def extract(self, paths):
        values = {c['metric']: None for c in self.cfg['constraints']}
        diagnostics = {}
        for kind in CELLS:
            job = 'DTMOS_' + kind + '_NOMINAL'
            d = diagnostics[kind] = {}
            if job not in paths:
                d['error'] = 'Missing successful simulation job'
                continue
            raw = Path(paths[job]) / 'raw'
            try:
                dc = engine.dc(raw / 'dcOp.dc')
                power = 900 * (-dc['VDD_SRC:p'] + dc['VSS_SRC:p'])
                if not math.isfinite(power):
                    raise ValueError('Nonfinite rail power')
                values[kind + '_Rail_power_mW'] = float(power)
                d['rail_power_mW'] = float(power)
                d['dc_operating_point'] = {k: v for k, v in dc.items() if k in ['IN', 'OUT', 'DUT.N1', 'DUT.N2', 'DUT.PB1', 'DUT.PB2', 'DUT.NB0', 'DUT.NB3', 'DUT.PLP', 'DUT.PHP', 'VDD_SRC:p', 'VSS_SRC:p', 'VOUT_SENSE:p'] or re.match(r'DUT.Mpb[1-4]:[bdgs]$', k)}
            except (OSError, ValueError, KeyError, IndexError) as e:
                d['dc_error'] = str(e)
            try:
                freq, ac = engine.read_wave(raw / 'ac.ac', ['VOUT_SENSE:p'])
                gain = abs(ac['VOUT_SENSE:p'])
                if len(freq) != len(gain) or len(freq) < 3 or not np.all(np.isfinite(gain)) or np.any(gain <= 0) or np.any(np.diff(freq) <= 0):
                    raise ValueError('Invalid AC response')
                band = (freq >= 100) & (freq <= 1000)
                slope = float(np.polyfit(np.log10(freq[band]), np.log10(gain[band]), 1)[0])
                d.update(gain_1Hz_AA=float(gain[0]), gain_500Hz_AA=float(np.interp(np.log10(500), np.log10(freq), gain)), gain_1kHz_AA=float(np.interp(3, np.log10(freq), gain)), log_magnitude_slope_100_to_1000Hz=slope)
                d['fractional_order_validation'] = 'DIAGNOSTIC_ONLY: slope does not certify unspecified fractional-order mapping'
                if kind == 'HPF':
                    cutoff = measure(freq, gain)
                    d['cutoff_measurement'] = cutoff
                    values['HPF_cutoff_Hz'] = cutoff['cutoff_Hz']
            except (OSError, ValueError, KeyError, IndexError, TypeError) as e:
                d['ac_error'] = str(e)
            try:
                tim, tr = engine.read_wave(raw / 'tran.tran.tran', ['VOUT_SENSE:p'])
                wave = tr['VOUT_SENSE:p']
                if len(tim) != len(wave) or len(tim) < 2 or tim[-1] < .06 - 1e-9 or tim[0] > .04 or not np.all(np.isfinite(wave)):
                    raise ValueError('Incomplete or invalid transient')
                ts = np.arange(10000) * 2e-6 + .04
                yy = -np.interp(ts, tim, wave)
                co = np.fft.rfft(yy - yy.mean()) / len(yy) * 2
                harmonics = np.abs(co[np.arange(1, 21) * 10])
                if harmonics[0] <= 0:
                    raise ValueError('Zero fundamental; THD undefined')
                thd = float(100 * np.linalg.norm(harmonics[1:]) / harmonics[0])
                if not math.isfinite(thd):
                    raise ValueError('Nonfinite THD')
                d.update(transient_complete_s=float(tim[-1]), input_frequency_Hz=500, input_peak_to_peak_uA=10, output_DC_uA=float(yy.mean() * 1e6), output_fundamental_peak_uA=float(harmonics[0] * 1e6), output_thd_2_to_20_percent=thd)
                if kind == 'HPF':
                    values['THD_500Hz_10uApp_percent'] = thd
            except (OSError, ValueError, KeyError, IndexError) as e:
                d['transient_error'] = str(e)
        return values, diagnostics

    def plan_text(self):
        annotation = '\n'.join('// ' + v['name'] + ' [' + v['unit'] + '] -> ' + ','.join(v['binding']['instances']) + '.' + v['binding']['parameter'] for v in self.variables)
        return ('// Frozen 17-MOS core and 20-MOS derived HPF, matched sizing in both jobs.\n'
                '// Width variables are total width; M3 keeps m=2 and per-finger w=total/2.\n'
                '// No topology, stimulus, model, supply, temperature, or cutoff criterion changes.\n'
                + annotation + '\n' + self.templates['HPF'])
