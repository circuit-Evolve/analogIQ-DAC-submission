<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`pa1088_dac_task_001`):** 18 metric types; **162 unique expanded scalar checks** (162 deterministic + 0 MC statistics). The evaluator has 18 constraint definitions and 162 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `pa1088_dac_task_001` now has 17 independent sizing variables, 18 scalar targets, 9 conditions and 18 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready_unproven`. The retained reference is outside the standard search bounds; it is not an in-bounds solution witness. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# pa1088_tb_small_signal_dac: verified golden sizing

Promoted 2026-11-05: **18 metrics, 9 saved conditions, 18 simulation jobs, 162/162 checks passing**.

Paper-referenced targets with the approved 15% allowance, using explicit minimum/maximum/range directions. dB limits use the underlying voltage or power ratio; strict stability limits remain K>1 and |Delta|<1. No limits were recalibrated to these golden results. See qualifications.json for reference exceptions.

The fixed sizing is recorded in `designs/start.json` (pack) and `golden_sizing/golden_design.json` (golden). Measurement expressions, conditions and exact simulation decks are in the pack; `saved_results.json` contains the verified values. Paper references are preserved in the circuit/golden `paper` directories.

The source_snapshot.json, schematic/oa and saved_setup files are historical source archives from the original Maestro import. They are not updated Cadence views. The revised golden_design.json, DUT netlists and replay decks are authoritative for this promotion.

- Full-precision sizing is required: worst bandwidth is 95.086464 MHz against 95.0079 MHz minimum, and worst power gain is 22.727869 dB against 22.717189257142927 dB minimum.
- The paper reports 111.774 MHz bandwidth while its reported edge difference is 110.774 MHz; the retained target uses the explicitly reported bandwidth.
- Stability is checked over the retained 1 MHz to 1 GHz span with strict K>1 and |Delta|<1. The source span begins at 1 Hz; no claim is made outside the simulated span.
- Psat and peak PAE are maxima over the retained input-power sweep. The paper uses the slow BJT section; all three supplied BJT model sections are tested here. Zin and Zout remain excluded.

From the task pack: `python3 runner.py designs/start.json /tmp/pa1088_dac_task_001_validation --validate-only`; use `--saved` to export stored values, or omit it to rerun all simulations into an empty output directory outside the pack.
