* analogiq 0.1.0 testbench - generated, do not edit
* task ota3s24_task_001  topology ota3s24
* recipe amp_dc_v1 v3  condition NN_T27_S1p00_CL0 (models NN, 27 C, supply 1.8 V)
* request ota3s24_task_001__plan  candidate 25f7ea5cdf3edbba
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc p_sup find par('-v(vdd)*i(VSUP)+-v(vss)*i(VNEG)') at=0.45
.measure dc i_sup find par('-i(VSUP)') at=0.45
.measure dc vo_lo find v(out) at=0.0
.measure dc vo_hi find v(out) at=1.2
.measure dc v_off find par('v(out)-v(inp)') at=0.45
.measure dc p_bias find par('-v(b_VB1)*i(VB_VB1)+-v(b_VB2)*i(VB_VB2)+-v(b_VB3)*i(VB_VB3)') at=0.45
