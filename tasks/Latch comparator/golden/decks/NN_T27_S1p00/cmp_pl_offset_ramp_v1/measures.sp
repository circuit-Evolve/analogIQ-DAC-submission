* analogiq 0.1.0 testbench - generated, do not edit
* task cmppl24_task_001  topology cmppl24_upcon2022
* recipe cmp_pl_offset_ramp_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request golden_cmppl24_task_001  candidate eca5dc39e87484f5
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs.
* Results: input.measure. Raw samples only; pass/fail rules are applied by analogiq.
.option measdgt=10
.measure tran chk_clk_edge when v(clk)='0.5*vdd_v' rise=1
.measure tran c002_vd_end find v(outp,outn) at=2.9800000000000005e-09
.measure tran c003_vd_end find v(outp,outn) at=3.98e-09
.measure tran c004_vd_end find v(outp,outn) at=4.98e-09
.measure tran c005_vd_end find v(outp,outn) at=5.9800000000000004e-09
.measure tran c006_vd_end find v(outp,outn) at=6.98e-09
.measure tran c007_vd_end find v(outp,outn) at=7.980000000000001e-09
.measure tran c008_vd_end find v(outp,outn) at=8.980000000000002e-09
.measure tran c009_vd_end find v(outp,outn) at=9.98e-09
.measure tran c010_vd_end find v(outp,outn) at=1.0980000000000001e-08
.measure tran c011_vd_end find v(outp,outn) at=1.1980000000000002e-08
.measure tran c012_vd_end find v(outp,outn) at=1.2980000000000001e-08
.measure tran c013_vd_end find v(outp,outn) at=1.3980000000000002e-08
.measure tran c014_vd_end find v(outp,outn) at=1.4980000000000002e-08
.measure tran c015_vd_end find v(outp,outn) at=1.598e-08
.measure tran c016_vd_end find v(outp,outn) at=1.698e-08
.measure tran c017_vd_end find v(outp,outn) at=1.7980000000000003e-08
.measure tran c018_vd_end find v(outp,outn) at=1.8980000000000002e-08
.measure tran c019_vd_end find v(outp,outn) at=1.998e-08
.measure tran c020_vd_end find v(outp,outn) at=2.0980000000000003e-08
.measure tran c021_vd_end find v(outp,outn) at=2.1980000000000002e-08
.measure tran c022_vd_end find v(outp,outn) at=2.298e-08
.measure tran c023_vd_end find v(outp,outn) at=2.3980000000000004e-08
.measure tran c024_vd_end find v(outp,outn) at=2.4980000000000003e-08
.measure tran c025_vd_end find v(outp,outn) at=2.5980000000000002e-08
.measure tran c026_vd_end find v(outp,outn) at=2.698e-08
.measure tran c027_vd_end find v(outp,outn) at=2.7980000000000003e-08
.measure tran c028_vd_end find v(outp,outn) at=2.8980000000000002e-08
.measure tran c029_vd_end find v(outp,outn) at=2.998e-08
.measure tran c030_vd_end find v(outp,outn) at=3.098e-08
.measure tran c031_vd_end find v(outp,outn) at=3.198e-08
.measure tran c032_vd_end find v(outp,outn) at=3.298e-08
.measure tran c033_vd_end find v(outp,outn) at=3.398e-08
.measure tran c034_vd_end find v(outp,outn) at=3.498e-08
.measure tran c035_vd_end find v(outp,outn) at=3.598e-08
.measure tran c036_vd_end find v(outp,outn) at=3.698e-08
.measure tran c037_vd_end find v(outp,outn) at=3.798e-08
.measure tran c038_vd_end find v(outp,outn) at=3.898e-08
.measure tran c039_vd_end find v(outp,outn) at=3.998e-08
.measure tran c040_vd_end find v(outp,outn) at=4.098e-08
.measure tran c041_vd_end find v(outp,outn) at=4.198e-08
