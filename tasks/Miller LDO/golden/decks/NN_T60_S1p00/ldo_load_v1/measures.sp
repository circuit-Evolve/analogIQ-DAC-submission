* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24m_miller_task_001  topology ldo24m_miller
* recipe ldo_load_v1 v1  condition NN_T60_S1p00 (models NN, 60 C, supply 2.1 V)
* request golden_ldo24m_miller_task_001  candidate 92722af89d1a6403
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vo_lo find v(out) at=0.0
.measure dc vo_hi find v(out) at=0.07
.measure dc ig_lo find par('-i(VIN)-iload') at=0.0
