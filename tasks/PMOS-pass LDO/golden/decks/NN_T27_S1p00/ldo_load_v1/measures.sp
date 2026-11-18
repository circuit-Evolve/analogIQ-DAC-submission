* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_load_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.7 V)
* request golden_ldo24c_conventional_task_001  candidate 92f6c13c43387af9
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vo_lo find v(out) at=9e-06
.measure dc vo_hi find v(out) at=0.0011
.measure dc ig_lo find par('-i(VIN)-iload') at=9e-06
