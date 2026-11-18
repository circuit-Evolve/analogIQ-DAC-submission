<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`gmc_reconstructed_131126_task_001`):** 6 metric types; **54 unique expanded scalar checks** (54 deterministic + 0 MC statistics). The evaluator has 6 constraint definitions and 54 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# Gm-C reconstructed fourth-order low-pass filter

Task: `gmc_reconstructed_131126_task_001`. Batch: `13_11_26`. PDK: Cadence gpdk090 v4.6 (90 nm).

This is the user-approved **experimental reconstruction**, not a paper-exact Fig.3 implementation. It contains four identical 32-MOS OTA cores, sixteen diode-feedback MOS and four differential capacitors: **144 MOS + 4 capacitors**. Connectivity and saved sizing are unchanged during import.

The benchmark exposes **69 variables**: 44 W/L, 22 matched multipliers, two capacitor values and one global VT bias. The saved candidate has every multiplier equal to 1. Standard physical bounds apply; public exports start at W=L=1 µm, m=1, C=1 pF and VT=0.5 V. Known sizing is curator-only in the matching golden package.

## Metrics and conditions

| Metric | Paper reference | Adopted limit |
|---|---:|---:|
| OTA differential gain | 39 dB | ≥33.15 dB |
| OTA UGF | 10 GHz | ≥8.5 GHz |
| OTA phase-margin estimate | 79° | 67.15–90.85° |
| OTA common-mode gain | −24 dB | ≤−20.4 dB |
| Filter cutoff | 15 MHz | 10–20 MHz |
| Filter input noise at assumed 1 MHz | 85 nV/√Hz | ≤97.75 nV/√Hz |

Nine independent conditions: NN/SS/SF/FS/FF at 1 V,27°C; NN at 0.9 and 1.1 V,27°C; NN at 1 V,−40 and 85°C. NN/1 V/27°C is nominal. These are separate variations, not a Cartesian grid. Input common mode and VREF track VDD/2; VT remains one common candidate value.

The literal-dB bounds above are the explicitly approved per-task exception to AnalogIQ's general linear-domain dB-tolerance rule. Cutoff uses the explicit 10–20 MHz range. Other target directions and limits retain the approved 15% policy. PM is a standalone-OTA unity-feedback estimate, not an STB margin. Noise frequency is an explicit assumption.

## Validity and verification scope

All 54 scalar checks pass in the retained candidate. Its prior dense-sweep, finite PZ/step and frozen-model evidence is preserved under the golden package. Several margins are very narrow; do not round the stored sizing. No layout/parasitic qualification is claimed.

The official nominal G8 check finds **OTA2.M19, OTA3.M19 and OTA4.M19 in triode**, worst saturation margin **−6.1825 mV**. The user explicitly instructed on 2026-11-13: “Apply the same bypass; preserve the sizing.” Saturation is therefore **waived, not passed**, with diagnostics retained. Nominal junction and voltage gates remain enforced and pass. This is a sizing task with a saturation waiver, not full G8 physical qualification. See `validity_gate_waiver.json` and the final official result in the golden package.

## Running the task

From `<ANALOGIQ>`:

```sh
.venv/bin/python -m analogiq validate --task gmc_reconstructed_131126_task_001
.venv/bin/python -m analogiq size-eval --task gmc_reconstructed_131126_task_001 --design <candidate.json> --out <new-output-directory>
```

The testbench pack supplies `problem.json`, `designs/start.json`, and 27 parameterized decks under `testbenches/`. Golden files and reference-check evidence are in `golden/13_11_26/Filters/Fourth_order_Gm_C/Gm_C_reconstructed`. Repository-wide approval flags remain administratively unapproved, as for the existing imported tasks; CLI reference checks require `--allow-unapproved`.

Paper: Pugazhenthi R, Ananiah Durai S, Nabihah Ahmad, “Design of Fourth Order Gm-C Low-Pass Filter for Microsensor Readout,” IJIE 18(1),59–71(2026), DOI10.30880/ijie.2026.18.01.005. Full PDF and metric provenance are in the circuit/golden paper folders. Spectre netlists are authoritative; the included SVG is a topology overview, not a native OA schematic.
