# Case A Starter: Load Collapse

This working localhost service uses a bounded request queue and a configurable worker pool. It logs queue wait, compute time, and total service time without telling you which mechanism dominates on your VM.

## Baseline

First follow the [copy instructions](../README.md#copy-your-starter). Run commands in `~/ecpe170-project/load-collapse`.

In each terminal, first run `cd ~/ecpe170-project/load-collapse`.

In terminal 1:

```bash
python3 -u server.py --host 127.0.0.1 --port 17101 2>&1 | tee m0-server.log
```

In terminal 2:

**Starter correctness test:** this command verifies that the unmodified case still produces the required results.

```bash
python3 -m unittest -v test_contract.py 2>&1 | tee m0-correctness.txt
```

**Baseline customer symptom commands:** these two load tests compare light demand with concurrent demand. Together they show the baseline performance degradation the customer is concerned about: sharply worse tail latency as concurrency rises.

```bash
python3 load_test.py --host 127.0.0.1 --port 17101 --clients 1 --requests 24 --csv results/m0-baseline.csv \
  | tee m0-baseline-light.txt
python3 load_test.py --host 127.0.0.1 --port 17101 --clients 12 --requests 48 --csv results/m0-baseline.csv \
  | tee m0-baseline-concurrent.txt
```

Save the server log as well as these correctness and load-test files before editing. Upload them for M0. Stop the server in terminal 1 with Ctrl-C after collecting the baseline.

## Baseline Graph for M0

The benchmark commands above append CSV rows. Use a new results filename if you repeat a baseline session, and pass that same filename to the plotter; keep earlier evidence. From your personal case folder, install Matplotlib in a virtual environment and plot your saved baseline:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install matplotlib
python plot_results.py results/m0-baseline.csv --save results/m0-baseline.png --no-show
```

Omit `--no-show` to also open a graph window on a desktop VM. Upload `results/m0-baseline.png` and its input CSV file(s) with the command/output receipts. In `m0-response`, describe one relationship visible in the graph and what it does **not** yet establish about the cause. A graph documents the symptom; it does not prove a diagnosis.

## Evidence Contract

- Keep `--database-size`, `--dimension`, and `--seed` identical for a comparison.
- Do not omit errors when calculating throughput.
- Match client request IDs to server telemetry.
- Use at least five repeated final runs under light and concurrent load.
- Rerun `test_contract.py` after every intervention.

The defaults use Python’s standard library and run natively on AMD64 and ARM64 Ubuntu. Exact timings depend on VM resources. You may instrument or restructure the service, but do not replace the customer workload with easier work and call it a speedup.
