from dtmos_corners import Task as Base
from robust_metrics import apply_directions, gain_spec

class Gain200Task(Base):
    mode='gain200'
    def __init__(self,profile='search_full'):
        super().__init__(profile)
        apply_directions(self.cfg['constraints'])
        gain=gain_spec(self.mode)
        gain['conditions']=[c['id'] for c in self.corners]
        self.cfg['constraints'].append(gain)
        self.cfg['description']+=' November10 gain interpretation: '+self.mode+'. Both gains and 50Hz attenuation, peaking, ripple, 500Hz gain are tracked. No added devices.'
        self.cfg['tracked_metrics']={
            'HPF_attenuation_50Hz_dB':{'approximate_graph_reference_dB':16,'reference_lower_dB':14.4,
                'source':'Fig5 low-frequency response near50Hz; approximate graph reading, diagnostic only'},
            'HPF_passband_ripple_dB':{'engineering_upper_dB':1,'source':'Existing2-20kHz cutoff qualification, not a paper target'},
            'HPF_gain_200Hz_dB':{'lower':-3.5,'upper':-2.5,'source':'User range; fixed-frequency interpretation'},
            'HPF_passband_gain_dB':{'lower':-3.5,'upper':-2.5,'source':'User range; passband interpretation'},
            'HPF_gain_500Hz_dB':{'source':'Fig4b transient comparison frequency; no unambiguous scalar target'},
            'HPF_peaking_dB':{'source':'Fig4a response shape; diagnostic only'}}

class PassbandTask(Gain200Task):
    mode='passband'
