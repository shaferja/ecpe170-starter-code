# Performance Emergency Room Starter Cases

These three directories contain working, correctness-tested starting systems for the individual Class Project. Copy your selected case plus the shared `common` folder into your personal project folder, then follow that case README. A Git repository or public remote is optional.

- [`load-collapse/`](load-collapse/README.md): investigate queueing, concurrency, and tail latency in a localhost service.
- [`fast-kernel-slow-product/`](fast-kernel-slow-product/README.md): investigate conversion, native-boundary, and workload-crossover costs.
- [`gpu-slower/`](gpu-slower/README.md): investigate transfer, compute, residency, batching, and routing with portable CPU evidence plus supplied accelerator traces.
- [`common/`](common/README.md): shared measurement helpers used by the case drivers.

## Copy Your Starter

Update the clean starter checkout, then replace `<case-directory>` below with `load-collapse`, `fast-kernel-slow-product`, or `gpu-slower`:

```bash
cd ~/ecpe170-starter-code
git pull --ff-only
mkdir -p ~/ecpe170-project
cp -R ~/ecpe170-starter-code/project-cases/common ~/ecpe170-project/
cp -R ~/ecpe170-starter-code/project-cases/<case-directory> ~/ecpe170-project/
cd ~/ecpe170-project/<case-directory>
```

Keep `common` beside your selected case, not inside it. Case A's load tester needs `../common/measurement.py`. If you already copied your case and `common` is missing, run only the `cp -R .../common ...` command above; preserve your existing case edits and evidence. Do your project work in the personal copy and leave the starter checkout unchanged.

These files are starting evidence, not an answer key. Do not assume a suspicious component is the dominant cause until an experiment distinguishes it from alternatives. Required work must remain native on AMD64 or ARM64 Ubuntu; a physical GPU is optional.
