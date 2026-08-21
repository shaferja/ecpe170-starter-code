# GPU and Fallback Trace Starter Packet

This packet supports Activities 18-19 through three equally valid evidence paths:
a real GPU run, a portable accelerated-library run, or the portable CPU benchmark
plus the committed GPU trace packet. Trace analysis is normal systems evidence, not
a lesser replacement for hardware access. Every path studies the same host/device
model, timing categories, and crossover question.

## Files

- `gpu_trace_packet.csv`: a fixed representative instructor trace with two GPU
  timing scenarios across several batch sizes. Treat it as trace evidence for the
  stated scenarios, not as a measurement from your own machine.
- `cpu_fallback_benchmark.py`: portable AMD64/ARM64 benchmark that emits the same
  timing-table shape while clearly labeling CPU analog measurements.
- `trace-analysis-template.md`: worksheet for comparing evidence paths and making a
  transfer/compute/total-time claim.

The trace columns are:

```text
evidence_path,batch_size,data_residency,h2d_ms,launch_compute_ms,d2h_ms,total_ms,notes
```

`launch_compute_ms` groups launch and useful compute because many teaching traces do
not separate those two values. `total_ms` is the end-to-end scope for the recorded
operation. It may exceed the three named components slightly because host-side
bookkeeping and timer boundaries also cost time.

## Portable CPU evidence

From this directory, run:

```bash
python3 cpu_fallback_benchmark.py --batch-sizes 1,8,32 \
  --vectors 256 --dimension 32 --trials 3
```

To create a CSV receipt:

```bash
mkdir -p results
python3 cpu_fallback_benchmark.py --batch-sizes 1,8,32 \
  --vectors 256 --dimension 32 --trials 3 \
  --csv results/cpu-fallback.csv
```

The CPU program uses the GPU-shaped columns as instrumentation analogs:
`h2d_ms` is host input copying, `launch_compute_ms` is a CPU function call plus exact
vector-search compute, and `d2h_ms` is result copying. These numbers are not fake GPU
measurements. Use them to practice separating scopes and to compare with
`gpu_trace_packet.csv`, which supplies representative instructor GPU evidence.

Use `--database-residency copy-each-trial` to model the extra cost of preparing the
database on every operation. The default, `resident`, prepares the database once.
This is a CPU analogy for reasoning about whether the vector index can remain on a
device across request batches.

## Optional hardware or accelerated-library evidence

If your environment has a real GPU or a portable accelerated library, record its
measurements with the same columns and name exactly what each timer includes. Do not
assume a compute-only timer is comparable with `total_ms`. Keep the CPU/trace path
available so the work remains reproducible on a personal Linux VM without a GPU.
