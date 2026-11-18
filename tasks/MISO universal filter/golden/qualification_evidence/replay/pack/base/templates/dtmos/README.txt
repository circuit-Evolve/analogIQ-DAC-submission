DTMOS paper-start adapter

The 17-device core and previously disclosed 20-device HPF remain frozen. Source decks are byte-identical at the seed. All original assumptions are copied in assumptions.json. Original scripts that write at import are never imported.

Shared sizing uses 25 variables: W/L of ten groups plus C1, C2, IB1, IB2, I0. W is total device width, and M3 uses fixed m=2, with half the total W per model instance. Bounds are optimizer search choices, not additional paper claims.

Matched groups: M2/M4; Mpb1–4; Mpb5/Mpb6/Mpb6_FB; Mpb7/Mpb8/Mpb8_FB; Mnb1/Mnb2; Mnb5/Mnb5_FB. M1, M3, Mnb3, Mnb4 have individual groups.

Variables (SI units):
M1_w: seed=3e-06, bounds=[7.5e-07,1.2e-05] m
M1_l: seed=2e-06, bounds=[5e-07,8e-06] m
M24_w: seed=5e-06, bounds=[1.25e-06,2e-05] m
M24_l: seed=2e-06, bounds=[5e-07,8e-06] m
M3_w: seed=0.00015, bounds=[3.75e-05,0.0002] m
M3_l: seed=2e-06, bounds=[5e-07,8e-06] m
Mpb14_w: seed=1e-05, bounds=[2.5e-06,4e-05] m
Mpb14_l: seed=2e-06, bounds=[5e-07,8e-06] m
Mpb56_w: seed=4e-05, bounds=[1e-05,0.0001] m
Mpb56_l: seed=5e-07, bounds=[1.8e-07,2e-06] m
Mpb78_w: seed=8e-06, bounds=[2e-06,3.2e-05] m
Mpb78_l: seed=2e-06, bounds=[5e-07,8e-06] m
Mnb12_w: seed=1e-05, bounds=[2.5e-06,4e-05] m
Mnb12_l: seed=5e-07, bounds=[1.8e-07,2e-06] m
Mnb3_w: seed=1e-05, bounds=[2.5e-06,4e-05] m
Mnb3_l: seed=5e-07, bounds=[1.8e-07,2e-06] m
Mnb4_w: seed=3e-06, bounds=[7.5e-07,1.2e-05] m
Mnb4_l: seed=2e-06, bounds=[5e-07,8e-06] m
Mnb5_w: seed=1e-05, bounds=[2.5e-06,4e-05] m
Mnb5_l: seed=2e-07, bounds=[1.8e-07,8e-07] m
C1: seed=7e-08, bounds=[7e-09,7e-07] F
C2: seed=1.2e-07, bounds=[1.2e-08,1.2e-06] F
I0: seed=6e-05, bounds=[6e-06,0.00024] A
IB1: seed=0.00025, bounds=[2.5e-05,0.001] A
IB2: seed=1.5e-05, bounds=[1.5e-06,6e-05] A

Four retained constraints: core and HPF rail power separately 0.4464–0.5456 mW; HPF THD strictly <6%; measured HPF rising half-power cutoff 180–220 Hz. Diagnostic slopes and core THD are retained but not promoted to new objectives.

Cutoff helper copied byte-for-byte from original hpf_cutoff.py. It measures the passband reference at sqrt(2000*20000) Hz, requires <=1 dB passband span across 2–20 kHz and LF rejection, and accepts only the first rising half-power crossing. Missing cutoff remains None; no target-frequency substitution.

Full frozen AC 1 Hz–10 MHz and transient 0–60 ms (maxstep/strobe 2us) in both jobs. Preflight measured 7.89s wall time including two concurrent fresh simulations and extraction. Shared runner must delete trial raw after extraction, while retaining selected final evidence.

Preflight: ../.. relative pack is run root; see run/preflight/dtmos/proof.json. All 25 mutation checks pass; seed pin/size identity passes; fresh scalar values exactly match saved comparison. Baseline power remains above target, and cutoff is null with FAIL_NO_FLAT_HPF_PASSBAND as expected. No execution blocker.
