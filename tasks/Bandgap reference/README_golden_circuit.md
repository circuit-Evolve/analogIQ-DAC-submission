<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`sky130_bandgap_101126_task_001`):** 6 metric types; **90 unique expanded scalar checks** (90 deterministic + 0 MC statistics). The evaluator has 6 constraint definitions and 90 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `sky130_bandgap_101126_task_001` now has 43 independent sizing variables, 6 scalar targets, 15 conditions and 60 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready_conditional`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# SKY130 bandgap reference — fixed final sizing

Retained golden sizing imported on 2026-11-10, batch `10_11_26`. Task `sky130_bandgap_101126_task_001` has 15 configured conditions.

`golden_sizing/golden_netlist.scs` and `golden_design.json` preserve the final-sized design. `verification_result.json` records import replay verification. `testbench/` mirrors the standalone task.

The paper is in `paper/`. Schematic status is documented in `schematic/asset_status.json`; historical OA views are not the final sizing.

## Qualification scope

- Fixed replay of latest approved golden checkpoint; no new sizing, optimization bounds, corners, or G8 certification.
- Canonical decks are byte-for-byte copies; all external include directives are PDK models.
- Historic schematic assets are provenance only and have not been updated to final sizing.
- Canonical aggregate worst labels are preserved only in evidence; saved_results uses per-corner scalars and directional summaries use metric-aware bounds.
- 15/15 corners, 90/90 scalar checks including 15 startup guards in the source checkpoint.
- Physical M4 W/L, M13 W, and M11 W overrides are indispensable and included in fixed logical parameters and physical_netlist_table.json.
- Exactly 50 canonical decks: 15 nominal, 15 temperature, 15 startup, five shared process line sweeps.
- Startup: no nodeset, 0 V through 1 us, ramp by 2 us, hold to 1 ms; final 900–1000 us mean, ripple, and DC agreement guarded.
- Line sensitivity has original percent-per-volt numerical definition, without division by Vref. TC denominator is corner nominal DC Vref; temperature interval 19–120 C.
- Historical extraction-source configs under evidence may contain earlier bounds or scopes; bundle.json alone defines the imported final target scope and fixed sizing.
