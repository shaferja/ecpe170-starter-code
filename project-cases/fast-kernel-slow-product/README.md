# Case B Starter: Fast Kernel, Slow Product

This packet exposes three comparable paths:

- a pure Python reference;
- a native call that converts the nested-list database and query for every request;
- a reusable native index with preconverted NumPy queries.

The distinction makes boundary scope measurable without prescribing which product policy you should recommend.

## Build and Baseline

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy pybind11
PYTHON=python ./build_ext.sh
python -m unittest -v test_contract.py
mkdir -p results
python benchmark.py --vectors 8 256 4096 --dimension 32 --queries 12 --trials 5 --warmups 1 --csv results/baseline.csv
```

Preserve the generated extension only in your local environment; commit source and evidence, not architecture-specific `.so` files or `.venv/`.

## Evidence Contract

- Every row must report `correct=PASS`.
- Keep database, dimension, query count, seed, trials, and warmups fixed across a comparison.
- Do not describe `native_reused_index` as end-to-end if your proposed product cannot actually reuse the converted database or query representation.
- Test at least three workload sizes and identify where conclusions change.
- Rerun correctness and all final workloads after an intervention.

The C++ source uses portable C++20 and pybind11 and makes no x86-specific assumptions. Required builds must be native on AMD64 or ARM64 Ubuntu.
