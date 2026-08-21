# Cache, Compiler Output, and CPU Parallelism Starter Packet

This packet supplies the runnable examples for Activities 13-17. Required work
uses portable C++20, Python 3, and GNU OpenMP on native AMD64 (`x86_64`) or ARM64
(`aarch64`) Ubuntu. Record `uname -m`, the compiler version, the exact command,
and the timed scope with every measurement. Exact timings and the best thread or
batch count will vary by VM.

The examples deliberately separate three kinds of evidence:

- `cache_bench.cpp` and `batch_benchmark.py` compare data-access and work-grouping
  choices.
- `compiler_example.cpp` and `generate_assembly.sh` expose architecture-specific
  compiler output without requiring one instruction set.
- `search_parallel.cpp`, `race_reduction.cpp`, and `false_sharing.cpp` separate
  correct speedup, wrong answers caused by a race, and correct-but-slow sharing.

## Activity 13: cache locality

Compile once, then run the same arithmetic work in row-wise and strided order:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic cache_bench.cpp -o cache_bench
./cache_bench --rows 16384 --cols 256 --trials 7
```

The program prints the architecture, problem size, matching checksums, and median
milliseconds for each access pattern. A matching checksum supports comparable
work; it does not by itself prove that the timing is noise-free. Try larger sizes
if both patterns fit comfortably in cache or produce nearly identical medians.

## Activity 14: batching and blocking

This pure-Python benchmark keeps the total query count and database fixed while
changing batch size. It processes the database in explicit blocks:

```bash
python3 batch_benchmark.py --vectors 512 --dim 32 --queries 64 \
  --batch-sizes 1,4,16 --block-size 64 --warmups 1 --trials 5
```

Each row reports median compute milliseconds, compute latency per query, and
throughput. This is a compute-only experiment: it excludes service queue wait,
networking, and input generation. Later service work must add those scopes before
making user-visible latency claims. A larger batch is not guaranteed to win in a
Python teaching harness; a flat or worse result is still evidence to explain.

## Activity 15: architecture-aware compiler output

Generate unoptimized and optimized assembly on the architecture of the current VM:

```bash
chmod +x generate_assembly.sh
./generate_assembly.sh
diff -u assembly/compiler_example_O0.s assembly/compiler_example_O3.s | less
```

The required command uses the compiler's native output syntax on both AMD64 and
ARM64. Interpret roles such as function boundary, loop, load/store, arithmetic,
comparison, branch, and register use. Do not expect identical mnemonics across
architectures, and do not treat assembly line count as runtime evidence.

Optional AMD64 enrichment only: on a VM where `uname -m` reports `x86_64`, run
`./generate_assembly.sh --intel` to create Intel-syntax files. This option rejects
ARM64 intentionally and is never required.

## Activity 16: serial and parallel vector search

GNU OpenMP is required for this example:

```bash
g++ -std=c++20 -O3 -Wall -Wextra -Wpedantic -fopenmp \
  search_parallel.cpp -o search_parallel
./search_parallel --vectors 200000 --dim 64 --trials 5 --threads 1,2,4
```

Every parallel row compares its best index and squared distance with the serial
answer before reporting speedup. Reduce `--vectors` for a smoke test. Do not use a
fast row whose correctness column says `FAIL`.

## Activity 17: races, reductions, and false sharing

Compile and run the correctness hazard separately from the performance hazard:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -fopenmp \
  race_reduction.cpp -o race_reduction
./race_reduction --items 1000000 --repeats 5 --threads 4

g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -fopenmp \
  false_sharing.cpp -o false_sharing
./false_sharing --iterations 5000000 --trials 5 --threads 4
```

`race_reduction` contains an intentionally unsafe shared update for observation;
the reduction result is the correctness reference. One lucky correct race result
does not make the code safe. `false_sharing` compares compact per-thread counters
with counters separated onto 64-byte boundaries. Both versions should be correct;
only timing may differ, and noisy or reversed results should be reported honestly.
