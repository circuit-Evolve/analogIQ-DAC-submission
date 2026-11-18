#!/bin/bash
# usage: evaluate.sh design.json out_dir   -> out_dir/metrics.json
design="$(realpath "$1")"; out="$(realpath -m "$2")"   # before the cd
cd <ANALOGIQ> && exec <ANALOGIQ>/.venv/bin/python -m analogiq size-eval --task telescopic01_scl180_task_001 --design "$design" --out "$out" "${@:3}"
