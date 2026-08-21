---
title: "Case A Starter: Load Collapse"
type: "starter-code guide"
canvas-publishing:
  publish: false
---

# Case A Starter: Load Collapse

This working localhost service uses a bounded request queue and a configurable worker pool. It logs queue wait, compute time, and total service time without telling you which mechanism dominates on your VM.

## Baseline

Terminal 1:

```bash
python3 server.py --host 127.0.0.1 --port 17101 | tee baseline-server.log
```

Terminal 2:

```bash
python3 -m unittest -v test_contract.py
mkdir -p results
python3 load_test.py --clients 1 --requests 24 --csv results/baseline.csv
python3 load_test.py --clients 12 --requests 48 --csv results/baseline.csv
```

Stop the server with Ctrl-C. Preserve `baseline-server.log` and `results/baseline.csv` before editing.

## Evidence Contract

- Keep `--database-size`, `--dimension`, and `--seed` identical for a comparison.
- Do not omit errors when calculating throughput.
- Match client request IDs to server telemetry.
- Use at least five repeated final runs under light and concurrent load.
- Rerun `test_contract.py` after every intervention.

The defaults use Python’s standard library and run natively on AMD64 and ARM64 Ubuntu. Exact timings depend on VM resources. You may instrument or restructure the service, but do not replace the customer workload with easier work and call it a speedup.
