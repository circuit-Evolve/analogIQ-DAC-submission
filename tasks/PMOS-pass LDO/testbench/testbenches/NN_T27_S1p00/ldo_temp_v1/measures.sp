* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_temp_v1 v2  condition NN_T27_S1p00 (models NN, 27 C, supply 1.7 V)
* request ldo24c_conventional_task_001__plan  candidate 164e80879370aa97
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vmax max v(out)
.measure dc vmin min v(out)
.measure dc vnom find v(out) at=27.0
