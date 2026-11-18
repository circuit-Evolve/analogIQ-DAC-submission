<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`tia02_task_001`):** 5 metric types; **28 unique expanded scalar checks** (28 deterministic + 0 MC statistics). The evaluator has 26 constraint definitions and 28 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# Recovered TIA benchmark — 2026-11-12

Task `tia02_task_001`: shunt-feedback TIA with capacitive feedback and a negative-capacitance generator (Singh et al., DOI 10.1007/s10470-018-1246-x).

Restored under the existing AnalogIQ contract after the user's explicit change to **15% target tolerance**. The new sizing passes **26/26 scalar constraint entries**, **31/31 required measurement checks**, and all three **nominal** G8 checks. All 14 configured conditions are simulated; targets apply only where specified in the task. There are 18 independent variables (14 continuous + four matched MOS multiplier groups), six MOS instances and 17 simulation jobs per candidate.

**Qualification scope:** the formal G8 constraints apply at nominal. Some non-nominal points still flag saturation/cutoff or terminal voltage. The additional per-condition audit is retained in `golden_sizing/all_condition_operating_point_audit.json`. Do not describe this as physically qualified at every corner. A stricter all-condition search did not find a complete scalar-plus-physical match. No forward-junction flags remain in the retained candidate at the 14 checked operating points.

The existing power-reference reconciliation is preserved: 1.458 mW (1.8 V × 0.81 mA), rather than the paper's printed 0.81 mW. Only the tolerance changed; the reference values, topology and conditions did not. The comparison uses directional limits and the configured linear-domain conversion for dB metrics.

`golden_sizing/` contains the new design, netlist, verification results and decks. `testbench/` contains the standard-start sizing pack; known sizes are curator-only. The previous withdrawn design and old verification are preserved under `_superseded/2026-11-12/`. The source `final.scs` was not changed.
