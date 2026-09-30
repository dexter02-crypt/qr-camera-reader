#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -c 'import sys; assert (3,11) <= sys.version_info[:2] <= (3,14), "Use standard CPython 3.11-3.14"'
if [ -L .venv ]; then echo "Refusing a symlinked environment" >&2; exit 2; fi
if [ ! -e .venv ]; then "$PYTHON" -m venv .venv; fi
if [ ! -x .venv/bin/python ]; then echo "Incomplete environment; inspect .venv manually" >&2; exit 2; fi
.venv/bin/python -c 'from importlib.metadata import distributions; names={d.metadata["Name"].lower() for d in distributions()}; assert not names.intersection({"opencv-python","opencv-python-headless","opencv-contrib-python-headless"}), "Competing OpenCV provider; use a clean project environment"'
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
echo "Setup and local tests finished. Webcam verification is a separate step."
