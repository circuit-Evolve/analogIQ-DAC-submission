<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`nvm_chargepump_111126_task_001`):** 6 metric types; **162 unique expanded scalar checks** (162 deterministic + 0 MC statistics). The evaluator has 6 constraint definitions and 162 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `nvm_chargepump_111126_task_001` now has 60 independent sizing variables, 6 scalar targets, 27 conditions and 27 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `onboarded`. The retained reference is outside the standard search bounds; it is not an in-bounds solution witness. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# NVM charge pump — Golden sizing

Imported 2026-11-11 as `nvm_chargepump_111126_task_001` in batch `11_11_26`. **27/27 corners and 162/162 scalar checks pass the agreed limits. Physical qualification remains unresolved.**

The circuit has six cross-coupled pump stages: 24 MOS devices (12 native NMOS and 12 high-voltage PMOS), 12 flying capacitors and 6 holding capacitors, totaling 42 DUT devices. The testbench adds three voltage sources and a 1 MΩ load resistor, for 46 total devices. Sizing has 36 grouped fields; releasing the symmetry ties gives 66 individual device fields.

The authoritative selected sizing is in `golden_sizing/golden_netlist.scs` and `golden_sizing/golden_design.json`. The current Virtuoso schematic and Maestro setup are in `schematic/`, mapped through its private `cds.lib`. Native schematic sizing matches the verified netlist. The source paper and Figure 12/13 excerpt are in `paper/`.

The runnable pack is under `testbench/nvm_chargepump_111126_task_001/`; per-corner results, sizes and qualification evidence are under `golden_sizing/`.

## Qualification notes

- One common sizing passes all six adopted scalar targets at all 27 reconstructed Figure 12 corners (162/162 checks).
- Figure 13 contains measured extrema with blank specification columns. The user adopted these extrema as bounds; they are not author-defined specifications or a nominal ±10% contract.
- Vout uses 19 V ±10%; ripple uses an upper limit of 4.069 mV +10%. Lower input power/ripple and higher output power/efficiency are accepted. No additional percentage is applied to Figure 13 limits.
- The paper’s native 3.3 V NMOS type is preserved. Steady-state max |VGS| exceeds 3.3 V in 26/27 corners, reaching 4.16937 V; negative VGS also occurs during startup. Model-range and physical qualification remain unresolved. No G8, layout or reliability certification is claimed.
- Figure 12 is partly clipped. The approved reconstructed set is TT/FF/SS × 3.0/3.3/3.6 V × −40/27/125°C, with TT/3.3 V/27°C nominal.
- Reported rise time uses the 10–90% cycle-averaged startup envelope. Maestro uses first raw crossings; both pass all 27 corners, with at most 0.01747 µs difference. Nominal rise is 32.42 µs versus 14.68 µs in the paper, inside the adopted 9.24–39.29 µs range.
- Ripple is settled peak-to-peak over 295–300 µs. The paper’s 4.069 mV markers appear on a rising trace; that definition discrepancy remains disclosed.
- Paper transistor dimensions are incomplete. These sizes were obtained through authorized resizing. Six-stage topology, device types, 20 MHz clocks and 1 MΩ load remain unchanged.
- This is a fixed pack-local replay, not a registered shared optimization benchmark. There are 36 physically resizable grouped fields, frozen for replay; 66 individual device fields if symmetry ties are released.
