# Python/C++ Extension Starter Packet

This packet wraps the known-good kernel in `../02-cpp-kernel/` with pybind11. Use
the same activated Python environment for the build, import, correctness check,
and benchmark. The build discovers that Python's extension suffix instead of
hard-coding an AMD64 or ARM64 filename.

## 1. Confirm the interface contract

Read this before editing build commands:

```text
Python call:
  index, squared_distance = search_ext.find_nearest(vectors, query)

vectors:
  NumPy float64, C-contiguous, shape (vector_count, dimension), borrowed for call
query:
  NumPy float64, C-contiguous, shape (dimension,), borrowed for call
return:
  (smallest best index, squared Euclidean distance), returned by value
errors:
  reject empty, wrong-rank, wrong-dtype, noncontiguous, or mismatched inputs
copy behavior:
  the extension does not convert or retain inputs; Python prepares valid arrays
```

`search_ext.cpp` makes those checks visible. A caller can choose to convert data,
but that conversion belongs to the caller's measured scope.

## 2. Activate one environment and build

From this directory on your personal Linux VM:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy pybind11
chmod +x build_ext.sh
PYTHON=python ./build_ext.sh
```

If the course packages are already available in your intended environment, do not
create another one. Verify the interpreter first with `which python` and
`python -m pip --version`.

The generated filename resembles
`search_ext.cpython-3xx-<architecture>-linux-gnu.so`; the exact Python and platform
tags vary. Never copy an `x86_64` suffix into instructions for an `aarch64` VM.

## 3. Verify correctness before timing

```bash
PYTHON=python ./build_ext.sh
python compare_python_cpp.py
```

The comparison covers hand-checkable cases, the smallest-index tie rule, a seeded
generated case, and rejected invalid inputs. Fix any failed comparison before
interpreting performance.

## 4. Compare Python and native timing scopes

```bash
python benchmark_extension.py \
  --vectors 1 32 512 5000 --dimension 32 --queries 10 \
  --trials 7 --warmups 2 --seed 170 --format table
```

The table separates pure Python, native calls with preconverted arrays, and native
calls with NumPy conversion inside the timer. Input generation is excluded from
all three. Tiny inputs may be slower through the extension because a call boundary
has fixed overhead; larger inputs can amortize that cost.

## 5. Investigate one import-path failure safely

After a successful import from this directory, move to its parent and try the same
import, then return:

```bash
cd ..
python -c "import search_ext"
cd 03-python-cpp-extension
python -c "import search_ext; print(search_ext.__file__)"
```

The first command should fail because the extension directory is no longer on the
default import path. This is an import-path failure, not a compiler or kernel
failure. Do not rename or copy the generated extension to force an import.

## First checks when something fails

| Symptom | First check |
|---|---|
| `No module named pybind11` | `python -c "import pybind11; print(pybind11.__file__)"` |
| Python and pip disagree | `which python` and `python -m pip --version` |
| `Python.h` missing | `python -c "import sysconfig; print(sysconfig.get_paths()['include'])"` |
| Extension filename looks wrong | `python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"` |
| Build reports a compiler/linker error | Read the first error and rerun `PYTHON=python ./build_ext.sh` |
| `import search_ext` fails | `pwd`, `ls search_ext*`, and `python -c "import sys; print(sys.path[0])"` |

Ask the instructor or TA before changing multiple packages or copying `.so` files.
Bring the exact command, first error, `which python`, and expected extension suffix.
