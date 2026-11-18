* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24m_miller_task_001  topology ldo24m_miller
* recipe ldo_load_step_v1 v1  condition NN_T60_S1p00_s12_21_b (models NN, 60 C, supply 2.1 V)
* request ldo24m_miller_task_001__plan  candidate ac77f2a3c8da6cc8
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran v_pre1 find v(out) at=3.9960000000000004e-05
.measure tran v_min1 min v(out) from=4e-05 to=7.996e-05
.measure tran v_end1 find v(out) at=7.996e-05
.measure tran v_mid1 find v(out) at=7.6e-05
.measure tran xa1 when v(out)='v_end1+0.0012' cross=last from=4e-05 to=7.996e-05
.measure tran xb1 when v(out)='v_end1-0.0012' cross=last from=4e-05 to=7.996e-05
.measure tran v_max2 max v(out) from=8e-05 to=0.00011996000000000001
.measure tran v_end2 find v(out) at=0.00011996000000000001
.measure tran v_mid2 find v(out) at=0.00011600000000000001
.measure tran xa2 when v(out)='v_end2+0.0012' cross=last from=8e-05 to=0.00011996000000000001
.measure tran xb2 when v(out)='v_end2-0.0012' cross=last from=8e-05 to=0.00011996000000000001
