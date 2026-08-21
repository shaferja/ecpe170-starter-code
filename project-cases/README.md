# Performance Emergency Room Starter Cases

These three directories contain working, correctness-tested starting systems for the individual Class Project. Copy only your selected case into your personal project repository, preserve the original in an initial commit, and follow that case README.

- [`load-collapse/`](load-collapse/README.md): investigate queueing, concurrency, and tail latency in a localhost service.
- [`fast-kernel-slow-product/`](fast-kernel-slow-product/README.md): investigate conversion, native-boundary, and workload-crossover costs.
- [`gpu-slower/`](gpu-slower/README.md): investigate transfer, compute, residency, batching, and routing with portable CPU evidence plus supplied accelerator traces.
- [`common/`](common/README.md): shared measurement helpers used by the case drivers.

These files are starting evidence, not an answer key. Do not assume a suspicious component is the dominant cause until an experiment distinguishes it from alternatives. Required work must remain native on AMD64 or ARM64 Ubuntu; a physical GPU is optional.
