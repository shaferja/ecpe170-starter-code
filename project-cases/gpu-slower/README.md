# Case C Starter: GPU Slower End to End

The standard complete path uses runnable CPU measurements plus an instructor-provided accelerator trace. A physical GPU is optional and must use the same timing-scope fields if added.

## Baseline

First follow the [copy instructions](../README.md#copy-your-starter). Run commands in `~/ecpe170-project/gpu-slower`.

**Starter correctness test:** this command verifies the portable CPU path and policy-analysis contract.

```bash
python3 -m unittest -v test_contract.py 2>&1 | tee m0-correctness.txt
```

**Baseline customer symptom commands:** these commands collect local CPU measurements and separately compare CPU/GPU paths within the supplied trace under GPU-all and hybrid policies. Do not calculate speedups between your VM timings and the trace: they come from different environments. Together they show the baseline degradation the customer is concerned about: faster accelerator compute can still produce slower end-to-end requests when transfer, launch, residency, and batch effects are included.

```bash
python3 cpu_baseline.py --batch-sizes 1,8,32,128 --vectors 512 --dimension 32 --trials 5 --csv results/m0-cpu.csv \
  | tee m0-baseline-cpu.txt
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy gpu-all \
  | tee m0-baseline-gpu-all.txt
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy hybrid --threshold 32 \
  | tee m0-baseline-hybrid.txt
python3 policy_analysis.py --trace gpu_trace_packet.csv --policy gpu-all --residency copy-each-request \
  | tee m0-baseline-gpu-copy.txt
```

The required path combines CPU measurements from your native VM with the supplied accelerator trace. Clearly label evidence provenance and upload the saved outputs for M0.

## Baseline Graph for M0

The benchmark commands above append CSV rows. Use a new results filename if you repeat a baseline session, and pass that same filename to the plotter; keep earlier evidence. From your personal case folder, install Matplotlib in a virtual environment and plot your saved baseline:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install matplotlib
python plot_results.py results/m0-cpu.csv --trace gpu_trace_packet.csv --save results/m0-baseline.png --no-show
```

Omit `--no-show` to also open a graph window on a desktop VM. Upload `results/m0-baseline.png` and its input CSV file(s) with the command/output receipts. In `m0-response`, describe one relationship visible in the graph and what it does **not** yet establish about the cause. A graph documents the symptom; it does not prove a diagnosis.

The graph separates your VM CPU measurements from instructor-provided trace panels for both residency assumptions. Upload `gpu_trace_packet.csv` as the trace input and preserve its provenance label.

## Evidence Contract

- Label `gpu_trace_packet.csv` as instructor-provided teaching evidence.
- Label `cpu_baseline.py` output as measured on your VM; do not compare its absolute values to the trace as though they came from one machine.
- Use trace rows for controlled GPU policy comparisons and your CPU results for portable workload reasoning.
- Keep H2D, compute, D2H, and total time distinct.
- Compare small, medium, and large batches and both residency assumptions.
- Rerun the correctness test and policy analysis after an intervention.

The starter hybrid threshold is an experimental scaffold, not the answer. A defensible intervention can change routing, threshold, batching, residency assumptions, or the portable CPU path, provided before/after evidence uses the same work and clearly states provenance.
