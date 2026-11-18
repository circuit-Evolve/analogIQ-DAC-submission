* analogiq 0.1.0 testbench - generated, do not edit
* task tia02_task_001  topology tia02_singh_2018
* recipe tia_dc_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request tia02_task_001__plan  candidate b4979bc7899dfdaa
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vo find v(out) at=-2e-05
.measure dc vo_lo find v(out) at=-2e-05
.measure dc vo_hi find v(out) at=-1e-06
.measure dc p_sup find par('-v(vdd)*i(VSUP)+-v(vss)*i(VNEG)') at=-2e-05
.measure dc i_sup find par('-i(VSUP)') at=-2e-05
