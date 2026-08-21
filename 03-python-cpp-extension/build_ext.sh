#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"
CXX="${CXX:-g++}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "ERROR: Python command not found: $PYTHON" >&2
  exit 1
fi
if ! command -v "$CXX" >/dev/null 2>&1; then
  echo "ERROR: C++ compiler not found: $CXX" >&2
  exit 1
fi
if ! "$PYTHON" -c 'import pybind11' >/dev/null 2>&1; then
  echo "ERROR: pybind11 is not importable by $PYTHON" >&2
  echo "Activate the intended virtual environment, then run:" >&2
  echo "  $PYTHON -m pip install pybind11 numpy" >&2
  exit 1
fi
if ! "$PYTHON" -c 'import numpy' >/dev/null 2>&1; then
  echo "ERROR: NumPy is not importable by $PYTHON" >&2
  echo "Activate the intended virtual environment, then run:" >&2
  echo "  $PYTHON -m pip install numpy" >&2
  exit 1
fi

EXT_SUFFIX="$("$PYTHON" -c \
  'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX") or ".so")')"
PYTHON_HEADER="$("$PYTHON" -c \
  'import pathlib, sysconfig; print(pathlib.Path(sysconfig.get_paths()["include"]) / "Python.h")')"
if [[ ! -f "$PYTHON_HEADER" ]]; then
  echo "ERROR: Python development header not found: $PYTHON_HEADER" >&2
  echo "On Ubuntu, install python3-dev for the Python used by this environment." >&2
  exit 1
fi

read -r -a PYBIND_INCLUDES <<< "$("$PYTHON" -m pybind11 --includes)"
OUTPUT="search_ext${EXT_SUFFIX}"

LINK_ARGS=()
if [[ "$(uname -s)" == "Darwin" ]]; then
  LINK_ARGS=(-undefined dynamic_lookup)
fi

"$CXX" \
  -O3 -Wall -Wextra -Wpedantic -shared -std=c++20 -fPIC \
  "${PYBIND_INCLUDES[@]}" -I../02-cpp-kernel \
  search_ext.cpp ../02-cpp-kernel/distance.cpp \
  ../02-cpp-kernel/search_kernel.cpp \
  "${LINK_ARGS[@]}" -o "$OUTPUT"

echo "python: $(command -v "$PYTHON")"
echo "built: $(pwd)/$OUTPUT"
"$PYTHON" -c \
  'import search_ext; print("imported:", search_ext.__file__); print("contract:", search_ext.boundary_contract)'
