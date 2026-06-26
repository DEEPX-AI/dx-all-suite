#!/usr/bin/env bash
# run.sh — one-command launcher for the YOLO26n construction-PPE retrain + DeepX benchmark.
# Uses the interpreter resolved by setup.sh (.venv_path) and runs pipeline.py, teeing to session.log.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

if [ ! -f "$SCRIPT_DIR/.venv_path" ]; then
    echo "ERROR: .venv_path missing. Run setup.sh first."
    exit 1
fi
PY="$(cat "$SCRIPT_DIR/.venv_path")"
if [ ! -x "$PY" ]; then
    echo "ERROR: interpreter $PY not executable. Re-run setup.sh."
    exit 1
fi

cd "$SCRIPT_DIR"
echo "==== Running YOLO26n construction-PPE retrain + DeepX benchmark pipeline ===="
echo "Interpreter: $PY"
"$PY" pipeline.py 2>&1 | tee session.log
echo "==== Pipeline finished. See report.md / results.json / sample_detect.jpg ===="
