# lelo_temp PTAT bias current generator (LELOTEMP_BIAS_IBP)

Bandgap-core PTAT current generator of the lelo_temp SKY130 temperature sensor: the OTA LELOTEMP_OTAR forces V(R1) = V(D1), and with an 8:1 PMOS mirror and a 1:8 substrate-PNP ratio the resistor ladder between VR1 and VD2 sees DeltaV = kT/q ln(64), giving a PTAT current of about 1 uA. Cascoded PMOS outputs (VCP from the OTA replica) deliver four IBP_1U currents to the relaxation oscillator/comparators, VD1 provides the CTAT voltage, and a self-disabling two-PMOS startup stack injects current into the diode branch at power-up.

- **Topology / sub-topology:** Blocks / Bias-voltage/current generator
- **Repository:** https://github.com/wulffern/lelo_temp_sky130a (commit `e439fe6b9351ea47a288847131337f483b2dbfcd`)
- **Top cell:** `LELOTEMP_BIAS_IBP` in `design/LELO_TEMP_SKY130A/LELOTEMP_BIAS_IBP.sch`
- **Device count:** 133 (95 MOSFET, 9 BJT, 16 R, 13 C)

## Files

- `metrics.xlsx`: sheet **Metrics** (performance numbers with sources) and sheet **Sizing** (every device with W/L/nf/m or value, file, line and permalink).
- `corners.xlsx`: sheet **Corner setup** (process/temperature/supply conditions defined in the repo) and sheet **Corner results** (values per corner).
- `schematics/`: schematic images listed below.

## Schematic images

- `schematics/01_LELOTEMP_BIAS_IBP.png`: Top level of the PTAT bias: startup PMOS stack (xsu1/xsu2), 8:1 PMOS mirror xca1[7:0]/xca2 with cascodes xca5/xca4 (gate VCP) into VD1 and VR1, regulating OTA xad6 (LELOTEMP_OTAR, VIN=VD1, VIP=VR1, output LPO), resistor ladder xd3[5:0] between VR1 and VD2, clamp NMOS xg1, 1:8 PNP pair xe1, cascoded outputs xca3[3:0]/xca2[3:0] -> IBP_1U[3:0], MIM caps xd1[9:0] on LPI and xd2[2:0] on VCP, dummies. Source: Rendered with xschem 3.4.4 from design/LELO_TEMP_SKY130A/LELOTEMP_BIAS_IBP.sch (https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/design/LELO_TEMP_SKY130A/LELOTEMP_BIAS_IBP.sch)
- `schematics/02_LELOTEMP_OTAR.png`: Sub-block xad6 LELOTEMP_OTAR: current-mirror OTA with LVT PMOS input pair, resistor tail, diode NMOS loads mirrored to the output, power-down switches, and the VCP cascode-bias replica on the right. Source: Rendered with xschem 3.4.4 from design/LELO_TEMP_SKY130A/LELOTEMP_OTAR.sch (https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/design/LELO_TEMP_SKY130A/LELOTEMP_OTAR.sch)
- `schematics/03_LELOTEMP_BIPOLAR.png`: Sub-block xe1 LELOTEMP_BIPOLAR: diode-connected substrate PNPs Q1 (x1) on VD1 and Q2[7:0] (x8) on VD2, pnp_05v5_W3p40L3p40. Source: Rendered with xschem 3.4.4 from design/LELO_TEMP_SKY130A/LELOTEMP_BIPOLAR.sch (https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/design/LELO_TEMP_SKY130A/LELOTEMP_BIPOLAR.sch)

## Notes

- Version check: the README results were regenerated in commit eacbd86 (2026-08-10). Later commits added 19 fill dummies and replaced the borrowed JNWBIAS_BIPOLAR cell with the identical LELOTEMP_BIPOLAR. Netlisting both versions with xschem and comparing them shows the 106 active devices (all except dummies with every terminal on a rail) have identical sizes and identical connectivity (graph isomorphism, ports pinned by name), so the results apply to this circuit. The leaf-cell library rey_atr_sky130a had its last design change on 2026-08-08, before the results. Device count today: 133 including 27 dummies (114 including 8 dummies at the results commit).
- All simulated numbers are schematic view only: summary.yaml has the Lay_* entries commented out and README.md has no Lay rows, so no post-layout block metrics exist.
- README spec rows are copied as written, including inconsistent ones (DC gain spec min 50 > typ 40; imax/imin spec typ 0.00). README marks DC gain (all rows), UGF Sch_etc min, VD Error Sch_3std min/max and idd Sch_etc max in red (outside spec).
- Sch_etc rows: min / median / max over 16 runs (summary.yaml method minmax); Sch_3std rows: mean - 3 sigma / mean / mean + 3 sigma over 30 MC runs (method 3std), per cicsim cmdsummary.py lines 50-64 (https://github.com/wulffern/cicsim/blob/c5e2d428a8e9c519a88b29a2722733e4625a7fe3/cicsim/cmdsummary.py#L50-L64).
- Corner token values (Tl/Th = -40/125 degC, Vl/Vt/Vh = 1.7/1.8/1.9 V) come from the external tech_sky130A repo (not vendored here); they agree with the top README key-parameter table (README.md lines 118-119: AVDD 1.7/1.8/1.9 V, temperature -40/27/125 C).
- The "DC gain" (lf_gain), gain margin, phase margin and UGF are loop-gain metrics of the closed PTAT regulation loop measured with a Tian probe between LPI and LPO, not open-loop OTA metrics.
- Sch testbenches include work/lpe/LELOTEMP_OTAR_lpe.spi (extracted OTA) before the xschem netlist work/xsch/LELOTEMP_BIAS_IBP.spice (lstb.spi/dc.spi lines 7-9, tran.spi lines 9-10).
- The PTAT current / Vc / DeltaV values at -40/25/125 degC are Python-model estimates quoted in LELOTEMP_BIAS_IBP.md (kind Design target), not simulations.
- Images: only the top schematic and its two custom sub-cells (LELOTEMP_OTAR, LELOTEMP_BIPOLAR) are shown. The LELOTEMP_BIAS_IBP_* schematics (BIP, CAP_LPI_A/B, CAP_VCP, N_G, OTA, P_CAS, P_CC, P_SRC, P_SU, R_LAD) are auto-generated layout-group wrappers that are not instantiated by LELOTEMP_BIAS_IBP.sch and only regroup the same devices, so they were omitted. REYATR_* leaf cells are single devices (sizes in _data/the Sizing sheet of metrics.xlsx).
- The repo .sym/.sch reference cpdk border symbols; they were resolved from github.com/wulffern/cpdk (cloned to scratch) for rendering only.
