# lelo_temp relaxation-oscillator timing comparator (LELOTEMP_CCMP)

Timing element of the lelo_temp relaxation oscillator: the comparator LELOTEMP_CMP plus a 5-unit MIM integrating capacitor on its VIP input, a reset NMOS (xg1, gate RST) and a power-down clamp NMOS (xg4). LELOTEMP_CMP is an unclocked two-stage comparator: PMOS input pair xp_diff1/xp_diff2 with a 3-unit PMOS tail, NMOS mirror load, NMOS common-source second stage xn_mirr_load5 with a PMOS current-source load, and no compensation capacitor, latch or clock, so it is a continuous-time open-loop comparator.

- **Topology / sub-topology:** Comparators / Continuous-time two-stage open-loop comparator (not on the sheet; own sub-topology)
- **Repository:** https://github.com/wulffern/lelo_temp_sky130a (commit `e439fe6b9351ea47a288847131337f483b2dbfcd`)
- **Top cell:** `LELOTEMP_CCMP` in `design/LELO_TEMP_SKY130A/LELOTEMP_CCMP.sch`
- **Device count:** 31 (26 MOSFET incl. 5 dummies, 5 MIM C)

## Files

- `metrics.xlsx`: sheet **Metrics** (performance numbers with sources) and sheet **Sizing** (every device with W/L/nf/m or value, file, line and permalink).
- `corners.xlsx`: sheet **Corner setup** (process/temperature/supply conditions defined in the repo) and sheet **Corner results** (values per corner).
- `schematics/`: schematic images listed below.

## Schematic images

- `schematics/01_LELOTEMP_CCMP.png`: Top cell: comparator instance x1_cmp (LELOTEMP_CMP), 5-unit MIM integrating capacitor xd1[4:0] on node IBP_1U[0] (VIP), reset NMOS xg1 (RST) and power-down clamp NMOS xg4 (PWRUP_N_1V8); VC drives VIN. Source: Rendered with xschem 3.4.4 from design/LELO_TEMP_SKY130A/LELOTEMP_CCMP.sch (https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/design/LELO_TEMP_SKY130A/LELOTEMP_CCMP.sch)
- `schematics/02_LELOTEMP_CMP.png`: Comparator LELOTEMP_CMP: PMOS input pair xp_diff1/xp_diff2, tail xp_mirr_tail3[2:0], NMOS mirror load xn_mirr_load2/3, second stage xn_mirr_load5 with PMOS load xp_mirr_tail2, bias mirror from IBP_1U, power-down devices, dummies xp_diff3[3:0] and xn_mirr_load0. Source: Rendered with xschem 3.4.4 from design/LELO_TEMP_SKY130A/LELOTEMP_CMP.sch (https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/design/LELO_TEMP_SKY130A/LELOTEMP_CMP.sch)

## Notes

- Not one of the listed sub-topologies; kept because it fits the Comparators topology and meets every other criterion.
- Device count includes 5 dummy transistors (xp_diff3[3:0] and xn_mirr_load0, all terminals on the supply rails); without them it is 26 devices.
- Testbench conditions: ibias = 1u per bias leg (replace.yaml line 3, https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/sim/LELOTEMP_CCMP/replace.yaml#L3), injected by IRAMP/ICMP (tran.spi lines 57-58, https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/sim/LELOTEMP_CCMP/tran.spi#L57-L58); threshold VC held at 0.75 V DC (replace.yaml line 7, https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/sim/LELOTEMP_CCMP/replace.yaml#L7); the bias block is replaced by these ideal sources (Makefile lines 7-9).
- Result rows: Sch_typ = single typical run; Sch_etc = min/median/max; Sch_3std = mean -/+ 3 sigma (summary.yaml lines 16-24, https://github.com/wulffern/lelo_temp_sky130a/blob/e439fe6b9351ea47a288847131337f483b2dbfcd/sim/LELOTEMP_CCMP/summary.yaml#L16-L24). No value in the table is marked out of spec.
- Version check: the README results were last regenerated in commit 57b0337 (2026-08-14); LELOTEMP_CCMP.sch and LELOTEMP_CMP.sch have no later changes, and the leaf-cell libraries they use (jnw_atr_sky130A, last design change 2025-02-27; jnw_tr_sky130A, no design change after 2026-08-10) are unchanged since, so the numbers describe this exact circuit.
- Corner token values (Tt = 27 degC, Th = 125, Tl = -40; Vt/Vl/Vh = 1.8/1.7/1.9 V) come from wulffern/tech_sky130A, which the repo pulls at revision main (config.yaml); the cited files last changed 2025-02-22 (temperature.spi), 2022-11-13 (supply.spi) and 2026-01-04 (cicsim.yaml), all before the results, so these are the values used.
- Leaf cells (JNWATR_*, JNWTR_CAPX1) are single devices whose sizes are in the Sizing sheet, so they are not imaged.
