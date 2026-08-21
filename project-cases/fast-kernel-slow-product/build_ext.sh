#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"
CXX="${CXX:-g++}"

command -v "$PYTHON" >/dev/null 2>&1 || { echo "ERROR: missing $PYTHON" >&2; exit 1; }
command -v "$CXX" >/dev/null 2>&1 || { echo "ERROR: missing $CXX" >&2; exit 1; }
"$PYTHON" -c 'import numpy, pybind11' >/dev/null 2>&1 || {
  echo "ERROR: NumPy and pybind11 must be importable by $PYTHON" >&2
  echo "Run: $PYTHON -m pip install numpy pybind11" >&2
  exit 1
}

EXT_SUFFIX="$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX") or ".so")')"
read -r -a INCLUDES <<< "$("$PYTHON" -m pybind11 --includes)"
EXTRA_LINK=()
if [[ "$(uname -s)" == "Darwin" ]]; then
  EXTRA_LINK=(-undefined dynamic_lookup)
fi

set -x
"$CXX" -O3 -std=c++20 -Wall -Wextra -Wpedantic -shared -fPIC \
  "${INCLUDES[@]}" native_search.cpp "${EXTRA_LINK[@]}" -o "case_b_native${EXT_SUFFIX}"
set +x

"$PYTHON" -c 'import case_b_native; print("import=PASS"); print(f"module={case_b_native.__file__}")'
