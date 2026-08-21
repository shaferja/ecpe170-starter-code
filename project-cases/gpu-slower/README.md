# Case C Starter: GPU Slower End to End

The standard complete path uses runnable CPU measurements plus an instructor-provided accelerator trace. A physical GPU is optional and must use the same timing-scope fields if added.

## Baseline

```bash
python3 -m unittest -v test_contract.py
mkdir -p results
python3 cpu_baseline.py --batch-sizes 1,8,32,128 --vectors 512 --dimension 32 --trials 5 --csv results/cpu-baseline.csv
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy gpu-all --residency database-resident
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy gpu-all --residency copy-each-request
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy hybrid --threshold 32 --residency database-resident
```

## Evidence Contract

- Label `gpu_trace_packet.csv` as instructor-provided teaching evidence.
- Label `cpu_baseline.py` output as measured on your VM; do not compare its absolute values to the trace as though they came from one machine.
- Use trace rows for controlled GPU policy comparisons and your CPU results for portable workload reasoning.
- Keep H2D, compute, D2H, and total time distinct.
- Compare small, medium, and large batches and both residency assumptions.
- Rerun the correctness test and policy analysis after an intervention.

The starter hybrid threshold is an experimental scaffold, not the answer. A defensible intervention can change routing, threshold, batching, residency assumptions, or the portable CPU path, provided before/after evidence uses the same work and clearly states provenance.
