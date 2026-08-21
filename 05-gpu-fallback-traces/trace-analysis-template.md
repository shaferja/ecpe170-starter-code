# GPU/Fallback Trace Analysis

Complete this worksheet for the evidence path your group used. Trace-based evidence,
portable-library evidence, and real-GPU evidence are evaluated by the same standard.

## Evidence receipt

| Field | Your evidence |
|---|---|
| Evidence path and file/command | |
| Machine architecture (`uname -m`) | |
| Batch sizes | |
| Data-residency assumption | |
| What `h2d_ms` includes | |
| What `launch_compute_ms` includes | |
| What `d2h_ms` includes | |
| What `total_ms` includes | |

## Comparison table

| Batch size | H2D ms | Launch/compute ms | D2H ms | Total ms | Total ms/query | Dominant cost |
|---:|---:|---:|---:|---:|---:|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## Reasoning

1. Where do fixed overheads dominate, and what evidence shows that?
2. How does batching amortize overhead? Include a per-query calculation.
3. How does keeping the index resident change the claim?
4. What can a compute-only timer support, and what can it not support?
5. What crossover or policy would you recommend for an interactive service?
