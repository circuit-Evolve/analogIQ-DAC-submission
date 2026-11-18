* analogiq 0.1.0 testbench - generated, do not edit
* task lcvco24_sheikhahmadi_task_001  topology lcvco24_sheikhahmadi
* recipe osc_tran_v1 v3  condition tt_T25_S1p00_startup (models tt, 25 C, supply 1.2 V)
* request golden_lcvco24_sheikhahmadi_task_001  candidate 18ad42aa3d408742
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran vavg avg v(outp,outn) from=8e-08 to=1.2e-07
.measure tran tper trig v(outp,outn) val='vavg' rise=1 td=8e-08 targ v(outp,outn) val='vavg' rise=11 td=8e-08
.measure tran vpp pp v(outp,outn) from=8e-08 to=1.2e-07
.measure tran vpp_a pp v(outp,outn) from=8e-08 to=1e-07
.measure tran vpp_b pp v(outp,outn) from=1e-07 to=1.2e-07
.measure tran tstart when par('abs(v(outp,outn)-vavg)')='0.45*vpp' rise=1
.measure tran pavg avg par('-v(vdd)*i(VSUP)') from=8e-08 to=1.2e-07
