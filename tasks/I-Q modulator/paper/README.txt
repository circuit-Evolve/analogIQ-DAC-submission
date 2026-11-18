TinyWhisper - analog IQ modulator / RF front-end (IHP SG13G2 130 nm)
=====================================================================
Design      : iqmod_top - two fully-differential 3rd-order MFB Butterworth low-pass filters
              (fc = 400 kHz, inverter-based Barthelemy/Manfredini OTA), SPDT input switches and two
              passive voltage-mode mixers driven by a 4-phase 25 % LO. Part of the TinyWhisper
              WSPR / multi-mode short-wave transmitter chip.
Designer    : Simon Dorrer, Johannes Kepler University (JKU)
Technology  : IHP SG13G2 130 nm CMOS (open PDK), VDD = 1.5 V
Repository  : https://github.com/iic-jku/TinyWhisper  (commit ad6cbaf, release v2026.08)
Archive DOI : https://doi.org/10.5281/zenodo.22115125
Macro folder: ihp130/macros/iqmod/

Contents
  Schematics/              23 schematic images (one per unique cell) + 00_hierarchy.txt
  Metrics.xlsx             'Metrics' and 'Sizing' sheets, every value with its repository source
  Corners.xlsx             'Corners' (supply sweep; PVT corners not run) and 'Monte Carlo' sheets
  Filter_design_notes.pdf  designer's derivation of the 3rd-order MFB filter
                           (repository file ihp130/macros/iqmod/scripts/filter_designer/3rd_order_mfb_lpf_designer.pdf)

Device count (full schematic hierarchy)
  548 devices including dummies: 456 MOSFETs, 80 rhigh resistor segments, 12 MIM capacitors
  316 devices excluding dummies: 256 MOSFETs, 48 resistor segments, 12 MIM capacitors

There is no journal paper for this design; the values come from the committed testbenches,
simulation data, CACE results and documentation in the repository.
