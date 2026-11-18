* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_line_v1 v4  condition NN_T27_S1p00_MC (Monte Carlo mismatch, 20 samples, seed 1; models NN, 27 C, supply 1.7 V)
* request ldo24c_conventional_task_001__plan  candidate 164e80879370aa97
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vout_nom find v(out) at=1.7
.measure dc ig_nom find par('-i(VIN)-iload') at=1.7
.measure dc vout_lo find v(out) at=1.7
.measure dc vout_hi find v(out) at=1.98
