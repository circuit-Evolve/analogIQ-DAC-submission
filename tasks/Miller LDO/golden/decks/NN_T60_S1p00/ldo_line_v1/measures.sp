* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24m_miller_task_001  topology ldo24m_miller
* recipe ldo_line_v1 v4  condition NN_T60_S1p00 (models NN, 60 C, supply 2.1 V)
* request golden_ldo24m_miller_task_001  candidate 92722af89d1a6403
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vout_nom find v(out) at=2.1
.measure dc ig_nom find par('-i(VIN)-iload') at=2.1
.measure dc vout_lo find v(out) at=2.1
.measure dc vout_hi find v(out) at=3.3
