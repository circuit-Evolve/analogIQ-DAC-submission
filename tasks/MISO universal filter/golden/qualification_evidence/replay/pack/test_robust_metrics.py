import unittest
import numpy as np
from robust_metrics import apply_directions, hpf_scalars, gain_spec, startup_score

class MetricsTests(unittest.TestCase):
 def test_directions(self):
  cs=[{'name':n,'lower':1,'upper':3} for n in ['Power_uW','TC_19_120_ppm_C','PSRR_LF_dB','Vref_V','BP_noise_in']]
  apply_directions(cs)
  self.assertEqual(cs[0]['lower'],0)
  self.assertEqual(cs[1]['lower'],0)
  self.assertIsNone(cs[2]['upper'])
  self.assertEqual(cs[3]['lower'],1)
  self.assertEqual(cs[4]['lower'],0)
 def test_fixed_frequency_not_moving_cutoff(self):
  f=np.geomspace(1,1e7,10001); h=(1j*f/200)/(1+1j*f/200)
  m=hpf_scalars(f,abs(h))
  self.assertAlmostEqual(m['HPF_gain_200Hz_dB'],-3.0103,places=3)
  self.assertLess(abs(m['HPF_passband_gain_dB']),.01)
  self.assertAlmostEqual(m['HPF_attenuation_50Hz_dB'],12.30,places=2)
 def test_distinct_branch(self):
  self.assertEqual(gain_spec('gain200')['name'],'HPF_gain_200Hz_dB')
  self.assertEqual(gain_spec('passband')['name'],'HPF_passband_gain_dB')
  self.assertEqual(gain_spec('gain200')['lower'],-3.5)
  self.assertEqual(gain_spec('passband')['upper'],-2.5)
 def test_invalid_wave(self):
  with self.assertRaises(ValueError):hpf_scalars([1,100],[1,1])
  with self.assertRaises(ValueError):hpf_scalars([1,200,20000],[1,np.nan,1])
 def test_startup_is_required(self):
  self.assertGreater(startup_score({'status':'completed','tail_mean_V':1.2,'tail_vpp_V':.1,'dc_relative_mismatch':0}),1)
  self.assertLessEqual(startup_score({'status':'completed','tail_mean_V':1.2,'tail_vpp_V':.0001,'dc_relative_mismatch':.001}),1)
  self.assertIsNone(startup_score({'status':'not_run_search'}))
if __name__=='__main__':unittest.main()
