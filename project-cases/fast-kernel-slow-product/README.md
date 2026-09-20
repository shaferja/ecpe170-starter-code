# Case B Starter: Fast Kernel, Slow Product

This packet exposes three comparable paths:

- a pure Python reference;
- a native call that converts the nested-list database and query for every request;
- a reusable native index with preconverted NumPy queries.

The distinction makes boundary scope measurable without prescribing which product policy you should recommend.

## Baseline

First follow the [copy instructions](../README.md#copy-your-starter). Run commands in `~/ecpe170-project/fast-kernel-slow-product`.

**Environment setup and build:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy pybind11
PYTHON=python ./build_ext.sh
```

**Starter correctness test:** this command verifies that the Python and native paths satisfy the same required contract.

```bash
python -m unittest -v test_contract.py 2>&1 | tee m0-correctness.txt
```

**Baseline customer symptom command:** this benchmark reports component and end-to-end timings across small, medium, and large workloads. Its rows show the baseline degradation the customer is concerned about: the impressive native-kernel speedup produces a much smaller product-level improvement for some workloads.

```bash
python benchmark.py --vectors 8 256 4096 --dimension 32 --queries 12 --trials 5 --warmups 1 --csv results/m0-baseline.csv \
  | tee m0-baseline-benchmark.txt
```

Save the unmodified correctness, component, and end-to-end timing rows before editing. Upload them for M0.

## Baseline Graph for M0

The benchmark commands above append CSV rows. Use a new results filename if you repeat a baseline session, and pass that same filename to the plotter; keep earlier evidence. From your personal case folder, install Matplotlib in a virtual environment and plot your saved baseline:

```bash
source .venv/bin/activate
python -m pip install matplotlib
python plot_results.py results/m0-baseline.csv --save results/m0-baseline.png --no-show
```

Omit `--no-show` to also open a graph window on a desktop VM. Upload `results/m0-baseline.png` and its input CSV file(s) with the command/output receipts. In `m0-response`, describe one relationship visible in the graph and what it does **not** yet establish about the cause. A graph documents the symptom; it does not prove a diagnosis.

## Evidence Contract

- Every row must report `correct=PASS`.
- Keep database, dimension, query count, seed, trials, and warmups fixed across a comparison.
- Do not describe `native_reused_index` as end-to-end if your proposed product cannot actually reuse the converted database or query representation.
- Test at least three workload sizes and identify where conclusions change.
- Rerun correctness and all final workloads after an intervention.

The C++ source uses portable C++20 and pybind11 and makes no x86-specific assumptions. Required builds must be native on AMD64 or ARM64 Ubuntu.
