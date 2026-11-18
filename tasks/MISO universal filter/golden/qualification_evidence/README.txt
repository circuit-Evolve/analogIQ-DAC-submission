MISO retained-nine golden sizing

45/45 metrics and 5/5 corners pass in fresh original-stimulus Spectre/OCEAN verification. Same physical design at every corner. All 600-point full measurements and 1200-point convergence results are preserved. See COMPARISON.txt, comparison.csv/json, policy.json and convergence.json.

Sizing rationale: independent A1/A2 OTA current and mirror sizing retains linearity while short, wide parallel input pairs and separate NMOS diode/output geometry reduce corner spread. The increased C2/C1 ratio stabilizes the slow-corner response; R3 centers the passband. These choices are supported by the saved five-corner measurements, not by the screen alone.

Replay (creates a new owned run; rejects reused label):
env -u PYTHONHOME -u PYTHONPATH <ANALOGIQ>/.venv/bin/python <WORK>/miso_iruwb_15pct_20261110/miso/nine_metric_sizing/selected/replay/run.py unique_replay_label

Replay uses the frozen engine9.py/physical.py, expanded actual geometry/current/passive bounds, explicit native input m16 and independent A1/A2 NMOS diode bindings. Legacy miso_problem.json is historical optimizer metadata, not the active nine-metric sizing recipe. The unchanged policy frequency definition retains an old 150-point baseline number; that is historical context, not the selected measurement. Current actual VM_BP decks and replay use 600 points/decade and convergence uses 1200. All actual 35 decks are in evidence, with exact common-design identities in deck_identity.json. Each corner raw.tar.gz holds raw waveforms; logs and extraction scripts/results remain beside it.

No LEDRO/external LLM, model/topology/supply/stimulus edits, corner retuning or removal of current copies. Prior 17-metric and initial 39/45 nine-metric artifacts remain unchanged outside this selection. Rejected exploratory runs remain in the parent directory and are not accepted evidence.
