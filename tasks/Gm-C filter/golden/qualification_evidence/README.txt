Gm-C FILTER — VERIFIED SIZING WITH 10–20 MHz CUTOFF RANGE
==============================================================================================================
All 9 independent conditions / 54 scalar checks pass, with one common sizing.
Scope: this qualifies the existing experimental reconstructed filter, NOT a paper-exact Fig.3 implementation.
Margins are narrow at several limits; this does not establish additional manufacturing or rounding margin.
UGF uses a minimum-only 15% target. Filter cutoff uses the explicit user-specified 10–20 MHz range.
Phase margin retains its two-sided 15% band; other metric directions remain unchanged.

Metric                         Unit       Paper       Allowed             Range across nine      Pass
--------------------------------------------------------------------------------------------------------------
OTA differential gain          dB               39  >= 33.15                33.1557..    54.5216  9/9
OTA UGF                        GHz              10  >= 8.5                  8.50141..    16.1139  9/9
OTA phase-margin estimate      deg              79  67.15..90.85            84.1807..    86.5416  9/9
OTA common-mode gain           dB              -24  <= -20.4               -26.7084..    -20.403  9/9
Filter cutoff                  MHz              15  10..20                  10.0021..    19.9975  9/9
Input noise at 1 MHz           nV/sqrtHz        85  <= 97.75                60.0408..    84.0219  9/9

Condition                Gain dB    UGF GHz     PM deg      CM dB     Fc MHz     Noise
--------------------------------------------------------------------------------------------------------------
NN_V0.9_T+27               44.375    10.5968    85.6798   -26.7084    12.9146    68.1043  PASS
NN_V1.0_T-40              33.9152     15.796    84.1807   -26.1507    18.5963    62.1184  PASS
NN_V1.0_T+27              47.8925    12.3705    85.5733   -25.4866    14.9488     74.566  PASS
NN_V1.0_T+85              35.6956    10.3661    86.2901   -24.8008     12.641    83.5386  PASS
NN_V1.1_T+27              45.9236     13.711    85.6397   -24.2151    16.5772    84.0219  PASS
SS_V1.0_T+27              54.5216    8.50141    85.0845      -26.1    10.0021    71.2468  PASS
SF_V1.0_T+27              33.1557    12.2358    86.5416    -25.486    12.8182    60.0408  PASS
FS_V1.0_T+27              52.1545    12.4624     85.141    -20.403    15.9869    80.8697  PASS
FF_V1.0_T+27              44.8791    16.1139     85.837    -25.149    19.9975    78.6106  PASS

Scope and limitations:
- Nine independent process, voltage and temperature conditions, not a 45-point Cartesian PVT grid.
- Original interpreted OTA connectivity unchanged. All four OTA instances use one global sizing.
- Filter is the disclosed experimental four-state reconstruction: four 32-MOS OTAs, 16 diode-feedback MOS and four differential capacitors. It is NOT a paper-exact Fig.3 reproduction.
- Noise evaluated at the existing assumed 1 MHz measurement point.
- Phase margin is the existing OTA unity-feedback estimate, not a full-filter STB margin.
- Dense scalar sweep: 500 points/decade. Fresh finite pole and small-step physical screens pass at all nine conditions.
- Physical screens check four dominant poles, reported poles in LHP, settling, rails and agreement with small-signal AC at outputs and internal bias nodes.
- Auxiliary pole screen: four lowest-magnitude poles real (imaginary part<1 Hz) and LHP, with fifth/fourth magnitude ratio>=3. Measured separation ratios are recorded per condition in physical_screen/summary.json.
- Original fixed 200 MHz screening result is retained in legacy_summary.json/legacy_screen.json; The fixed 200 MHz result is informational; it is not a scalar target; cutoff is separately checked against 10–20 MHz. Scalar limits are unchanged by this diagnostic.
- Finite PZ/transient checks are not unrestricted stability proof; installed BSIM3 PZ approximates frequency-dependent terms at1 Hz.
- No layout/parasitic extraction. Original libraries and curator AnalogIQ folder remain unchanged.

Sizing (SI units):
{
  "input_p_w": 1.616373198494229e-06,
  "input_p_l": 1e-07,
  "input_n_w": 6.91011125473508e-07,
  "input_n_l": 1e-07,
  "cross_n_w": 6.097387050451806e-07,
  "cross_n_l": 2.1971700680460613e-07,
  "cross_p_w": 5.76537527379325e-07,
  "cross_p_l": 1.2761518665623804e-07,
  "load_n_w": 3.312031907215333e-07,
  "load_n_l": 1.0581221839827198e-07,
  "load_p_w": 5.266863858166174e-07,
  "load_p_l": 1.6428751788715384e-07,
  "cm_out_n_w": 8.801419180712912e-07,
  "cm_out_n_l": 2.1179831998512523e-07,
  "cm_out_p_w": 2.460619766730277e-06,
  "cm_out_p_l": 1.1757870980803943e-07,
  "cm_node_n_w": 1.4197553124291605e-06,
  "cm_node_n_l": 4.783452882664011e-07,
  "cm_node_p_w": 8.748789928694398e-07,
  "cm_node_p_l": 3.556196510507261e-07,
  "cm_fb_n_w": 3.445955075140213e-07,
  "cm_fb_n_l": 2.88066950542238e-07,
  "cm_fb_p_w": 1.19871740118854e-06,
  "cm_fb_p_l": 1.9370711174580699e-07,
  "bias_n_w": 6.245442150019207e-07,
  "bias_n_l": 2.1967325249632536e-07,
  "bias_p_w": 2.922769224210927e-06,
  "bias_p_l": 2.379293521829501e-07,
  "cap_b_F": 7.884111169815835e-13,
  "cap_d_F": 3.2331646491198457e-12,
  "vt_bias_V": 0.5647580330549347,
  "M19_w": 1.8948106084351113e-06,
  "M19_l": 4.139611362942147e-07,
  "M23_w": 2.5646499510126416e-06,
  "M23_l": 4.7458098123342276e-07,
  "M20_w": 1.4532706843959067e-06,
  "M20_l": 2.697555715275229e-07,
  "M24_w": 2.4142877712775313e-06,
  "M24_l": 2.22979261268972e-07,
  "M25_w": 7.145921500956735e-07,
  "M25_l": 1.8376225872228054e-07,
  "M28_w": 3.130736243000742e-06,
  "M28_l": 2.511109326302167e-07,
  "feedback_n_w": 6.834583309357679e-07,
  "feedback_n_l": 1.0012820146194029e-07,
  "feedback_p_w": 1.031433708291801e-06,
  "feedback_p_l": 1e-07
}

Frozen extractor templates support extraction only; use packaged netlists to reproduce this reconstructed circuit.
Replay: cd to this folder and run replay.py --out <empty SSD directory> with the existing LEDRO Python environment.
Replay validates frozen inputs and numerical reproduction; see replay_result.json for the actual completed replay outcome.
