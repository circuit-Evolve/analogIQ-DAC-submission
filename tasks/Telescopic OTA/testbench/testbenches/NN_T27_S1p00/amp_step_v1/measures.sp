* analogiq 0.1.0 testbench - generated, do not edit
* task telescopic01_scl180_task_001  topology telescopic01_scl180
* recipe amp_step_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request telescopic01_scl180_task_001__plan  candidate 1ad1a1f9b5e47ce6
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran v_beg_1 find v(out) at=1.99e-07
.measure tran v_end_1 find v(out) at=3.9899999999999996e-07
.measure tran sr_1 trig v(out) val='v_beg_1+0.2*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.8*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran x_hi_1 when v(out)='(vc+og*step/2)+band' cross=last from=2e-07 to=3.9899999999999996e-07
.measure tran x_lo_1 when v(out)='(vc+og*step/2)-band' cross=last from=2e-07 to=3.9899999999999996e-07
.measure tran y_hi_1 when v(out)='v_end_1+band' cross=last from=2e-07 to=3.9899999999999996e-07
.measure tran y_lo_1 when v(out)='v_end_1-band' cross=last from=2e-07 to=3.9899999999999996e-07
.measure tran pk_1 max v(out) from=2e-07 to=3.9899999999999996e-07
.measure tran tg_1 min v(out) from=2e-07 to=3.9899999999999996e-07
.measure tran sw_1_00 trig v(out) val='v_beg_1+0.05*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.25*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_01 trig v(out) val='v_beg_1+0.1*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.3*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_02 trig v(out) val='v_beg_1+0.15*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.35*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_03 trig v(out) val='v_beg_1+0.2*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.4*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_04 trig v(out) val='v_beg_1+0.25*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.45*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_05 trig v(out) val='v_beg_1+0.3*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.5*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_06 trig v(out) val='v_beg_1+0.35*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.55*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_07 trig v(out) val='v_beg_1+0.4*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.6*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_08 trig v(out) val='v_beg_1+0.45*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.65*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_09 trig v(out) val='v_beg_1+0.5*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.7*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_10 trig v(out) val='v_beg_1+0.55*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.75*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_11 trig v(out) val='v_beg_1+0.6*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.8*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_12 trig v(out) val='v_beg_1+0.65*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.85*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_13 trig v(out) val='v_beg_1+0.7*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.9*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran sw_1_14 trig v(out) val='v_beg_1+0.75*(v_end_1-v_beg_1)' rise=1 td=2e-07 targ v(out) val='v_beg_1+0.95*(v_end_1-v_beg_1)' rise=1 td=2e-07
.measure tran v_beg_2 find v(out) at=3.9899999999999996e-07
.measure tran v_end_2 find v(out) at=5.99e-07
.measure tran sr_2 trig v(out) val='v_beg_2+0.2*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.8*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran x_hi_2 when v(out)='(vc-og*step/2)+band' cross=last from=4e-07 to=5.99e-07
.measure tran x_lo_2 when v(out)='(vc-og*step/2)-band' cross=last from=4e-07 to=5.99e-07
.measure tran y_hi_2 when v(out)='v_end_2+band' cross=last from=4e-07 to=5.99e-07
.measure tran y_lo_2 when v(out)='v_end_2-band' cross=last from=4e-07 to=5.99e-07
.measure tran pk_2 max v(out) from=4e-07 to=5.99e-07
.measure tran tg_2 min v(out) from=4e-07 to=5.99e-07
.measure tran sw_2_00 trig v(out) val='v_beg_2+0.05*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.25*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_01 trig v(out) val='v_beg_2+0.1*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.3*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_02 trig v(out) val='v_beg_2+0.15*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.35*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_03 trig v(out) val='v_beg_2+0.2*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.4*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_04 trig v(out) val='v_beg_2+0.25*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.45*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_05 trig v(out) val='v_beg_2+0.3*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.5*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_06 trig v(out) val='v_beg_2+0.35*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.55*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_07 trig v(out) val='v_beg_2+0.4*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.6*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_08 trig v(out) val='v_beg_2+0.45*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.65*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_09 trig v(out) val='v_beg_2+0.5*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.7*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_10 trig v(out) val='v_beg_2+0.55*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.75*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_11 trig v(out) val='v_beg_2+0.6*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.8*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_12 trig v(out) val='v_beg_2+0.65*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.85*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_13 trig v(out) val='v_beg_2+0.7*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.9*(v_end_2-v_beg_2)' fall=1 td=4e-07
.measure tran sw_2_14 trig v(out) val='v_beg_2+0.75*(v_end_2-v_beg_2)' fall=1 td=4e-07 targ v(out) val='v_beg_2+0.95*(v_end_2-v_beg_2)' fall=1 td=4e-07
