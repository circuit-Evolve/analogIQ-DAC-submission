<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`poweramp_dac_task_001`):** 7 metric types; **63 unique expanded scalar checks** (63 deterministic + 0 MC statistics). The evaluator has 7 constraint definitions and 63 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `poweramp_dac_task_001` now has 71 independent sizing variables, 7 scalar targets, 9 conditions and 18 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `sizing_task_verified_with_model_qualification_limits`. The retained reference is outside the standard search bounds; it is not an in-bounds solution witness. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# poweramp_tb_dac: verified golden sizing

Promoted 2026-11-05: **7 metrics, 10 saved conditions, 20 simulation jobs, 70/70 checks passing**.

Paper-referenced targets with the approved 15% allowance, using explicit minimum/maximum/range directions. dB limits use the underlying voltage or power ratio; strict stability limits remain K>1 and |Delta|<1. No limits were recalibrated to these golden results. See qualifications.json for reference exceptions.

The fixed sizing is recorded in `designs/start.json` (pack) and `golden_sizing/golden_design.json` (golden). Measurement expressions, conditions and exact simulation decks are in the pack; `saved_results.json` contains the verified values. Paper references are preserved in the circuit/golden `paper` directories.

The source_snapshot.json, schematic/oa and saved_setup files are historical source archives from the original Maestro import. They are not updated Cadence views. The revised golden_design.json, DUT netlists and replay decks are authoritative for this promotion.

- The approximate MMBT6429 model uses the paper VAF=804 V (previously 100 V); remaining model parameters are unchanged. The supplied models are not the exact author model library.
- Transresistance rm was removed at the user request after failing its target. Its output-stage ratio remains inlined in the retained original total-gain expression; no standalone rm metric is scored.
- Ten saved condition rows represent nine unique voltage/temperature conditions: Nominal duplicates VT_V42_T27. These are fixed-model VT corners, not process corners. Auxiliary +15 V, -7 V and +6 V supplies remain fixed.
- Q11 maximum absolute VCE is 49.2683 V versus the BC857C 45 V metadata. This is outside the seven retained metric checks; passing them is not hardware-stress qualification.
- All ten slew settling diagnostics passed. Physical component values in dut.scs are authoritative; legacy pa_* testbench declarations are retained for reproducibility and do not override literal DUT sizes.

From the task pack: `python3 runner.py designs/start.json /tmp/poweramp_dac_task_001_validation --validate-only`; use `--saved` to export stored values, or omit it to rerun all simulations into an empty output directory outside the pack.
