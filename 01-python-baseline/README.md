# Python Vector-Search Starter Packet

These portable Python files support Activities 04-08. Run them on your personal
Linux VM from this directory. They use no architecture-specific instructions and
work natively on AMD64 (`x86_64`) and ARM64 (`aarch64`) Ubuntu.

## Check correctness first

```bash
python3 -m unittest -v test_vector_search.py
python3 vector_search_baseline.py
```

The contract tests cover a one-vector input, a known nearest vector, an exact
zero-distance match, the smallest-index tie rule, empty/zero-dimensional input,
dimension mismatch, and agreement between nested and flat representations.

## Run a reproducible benchmark

```bash
python3 vector_search_benchmark.py \
  --vectors 2000 --dimension 32 --queries 10 \
  --trials 7 --warmups 2 --seed 170 \
  --representation nested --format table

python3 vector_search_benchmark.py \
  --vectors 2000 --dimension 32 --queries 10 \
  --trials 7 --warmups 2 --seed 170 \
  --representation flat --format csv > results-flat.csv
```

`--vectors` controls input size. The harness creates data and converts its
representation before starting the timer. Its reported timed scope is exact search
for all queries; setup and conversion are excluded.

Use the **Benchmark Reproducibility Receipt** page under **Resources** in the
Canvas course with every major claim. Record the exact command rather than reconstructing it later.

## Profile the search kernel

```bash
python3 profile_vector_search.py \
  --vectors 5000 --dimension 32 --queries 20 \
  --representation nested --output profile-nested.txt

head -n 25 profile-nested.txt
```

Input generation occurs before profiling starts. Compare nested and flat
representations by changing only `--representation`.

## Compare Python with NumPy

```bash
python3 numpy_vector_search.py \
  --vectors 5000 --dimension 32 --queries 10 \
  --trials 7 --warmups 2 --seed 170
```

The script verifies matching answers before timing. It reports both NumPy with
conversion included and NumPy with arrays already converted. This makes the Python
to native-library boundary visible instead of hiding conversion cost.

## Interpret output carefully

- Timing values depend on the VM and current system load; compare trends, not an
  instructor's exact number.
- Matching checksums help show that repeated trials performed the same work. They
  do not replace the small correctness tests.
- Always name what the timer includes and what it excludes.
- Keep private instructor expected outputs and grading anchors out of this folder.
