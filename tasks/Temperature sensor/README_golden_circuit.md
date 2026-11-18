<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`temp_sensor_101126_task_001`):** 6 metric types; **18 unique expanded scalar checks** (18 deterministic + 0 MC statistics). The evaluator has 18 constraint definitions and 18 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `temp_sensor_101126_task_001` now has 30 independent sizing variables, 18 scalar targets, 3 conditions and 3 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `needs_owner_decision`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# Temperature sensor — Block Design for an RFID Integrated Tag in an Open-Access Technology Node.

Retained golden sizing imported on 2026-11-10, batch `10_11_26`. Task `temp_sensor_101126_task_001` has 3 configured conditions.

`golden_sizing/golden_netlist.scs` and `golden_design.json` preserve the final-sized design. `verification_result.json` records import replay verification. `testbench/` mirrors the standalone task.

The paper is in `paper/`. Schematic status is documented in `schematic/asset_status.json`; historical OA views are not the final sizing.

## Qualification scope

- Only TT, FS, SF are active; FF and SS were excluded by the user.
- Targets are approximate digitized paper graph readings.
- PNP geometry is a retained modeling assumption because the paper omitted it.
- Endpoint sensitivity and output span are mathematically related; six metrics are 18 checks, not independent specifications.
- No sensor power target is asserted.
- Native final golden library is preserved, not historical baseline sizing.
