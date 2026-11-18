<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`ldo_erroramp_dac_task_001`):** 7 metric types; **105 unique expanded scalar checks** (105 deterministic + 0 MC statistics). The evaluator has 7 constraint definitions and 105 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `ldo_erroramp_dac_task_001` now has 37 independent sizing variables, 7 scalar targets, 15 conditions and 16 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# LDO_with_erroramp_tb_dac: verified golden sizing

Promoted 2026-11-05: **7 metrics, 15 saved conditions, 30 simulation jobs, 105/105 checks passing**.

Paper-referenced targets with the approved 15% allowance, using explicit minimum/maximum/range directions. dB limits use the underlying voltage or power ratio; strict stability limits remain K>1 and |Delta|<1. No limits were recalibrated to these golden results. See qualifications.json for reference exceptions.

The fixed sizing is recorded in `designs/start.json` (pack) and `golden_sizing/golden_design.json` (golden). Measurement expressions, conditions and exact simulation decks are in the pack; `saved_results.json` contains the verified values. Paper references are preserved in the circuit/golden `paper` directories.

The source_snapshot.json, schematic/oa and saved_setup files are historical source archives from the original Maestro import. They are not updated Cadence views. The revised golden_design.json, DUT netlists and replay decks are authoritative for this promotion.

- R8 and R11 are each 50 ohm, producing approximately 11.964 mA internal divider preload. The external 100 uA and 25 mA tests therefore have about 12.064 mA and 36.964 mA total load. Nominal no-external-load input is 12.504539 mA / 22.508171 mW; this is not a low-quiescent-current qualification.
- M9 bulk is tied to VIN, with its source still at net10. This documented connectivity correction follows the reference.
- PSR at 1 MHz uses the adopted 20 dB source design goal, not the source achieved -0.2 dB. Other target references and directions are explicit in targets.json.
- The retained legacy metric name Load Regulation (mV/V) has the corrected unit mV/A. Line regulation and unreferenced power/current/efficiency outputs are not active metrics.
- Verified numerical settings: reltol=1e-6, vabstol=1e-9, iabstol=1e-12, STB 100 points/decade.

From the task pack: `python3 runner.py designs/start.json /tmp/ldo_erroramp_dac_task_001_validation --validate-only`; use `--saved` to export stored values, or omit it to rerun all simulations into an empty output directory outside the pack.
