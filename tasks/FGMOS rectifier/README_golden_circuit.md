<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`fgmos_rectifier_101126_task_001`):** 4 metric types; **32 unique expanded scalar checks** (32 deterministic + 0 MC statistics). The evaluator has 4 constraint definitions and 32 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `fgmos_rectifier_101126_task_001` now has 33 independent sizing variables, 4 scalar targets, 8 conditions and 8 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `needs_owner_decision`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# FGMOS full-wave rectifier — Low Voltage Squarer/Divider Circuit based on FGMOS

Retained golden sizing imported on 2026-11-10, batch `10_11_26`. Task `fgmos_rectifier_101126_task_001` has 8 configured conditions.

`golden_sizing/golden_netlist.scs` and `golden_design.json` preserve the final-sized design. `verification_result.json` records import replay verification. `testbench/` mirrors the standalone task.

The paper is in `paper/`. Schematic status is documented in `schematic/asset_status.json`; historical OA views are not the final sizing.

## Qualification scope

- Conditional golden for these eight conditions only; not a full Cartesian process/temperature sweep.
- Power counts VDD only, excluding output-compliance and bias sources.
- AC bias is 17.5 uA; output compliance is 0.7 V; DC error is normalized to 35 uA full scale.
- Paper does not specify the exact AC bias, compliance, power setup or error normalization; retained interpretation is explicit.
- Final selected widths/lengths are rounded to 1 nm and capacitors to 1 fF; no new sizing.
- Preserves 1 Tohm floating-gate resistors and gmin=1e-15; physical floating-gate charge conditions are not established.
- Native final golden library was independently extracted and verified at all eight conditions.
