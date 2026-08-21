---
title: "ECPE 170 Student Starter Code"
type: "repository guide"
canvas-publishing:
  publish: false
---

<!-- {"tag": "publish-hide-next-line"} -->
# ECPE 170 Student Starter Code

This public repository is the student-facing source for ECPE 170 health checks, starter programs, traces, and worksheet templates. Files here are starting points for your own work, not answer keys. You remain responsible for understanding, testing, measuring, and explaining anything you use.

## Clone Once, Update Before Each Activity

During Linux VM setup, clone the repository into your home directory:

```bash
cd ~
git clone https://github.com/shaferja/ecpe170-starter-code.git
```

Before every activity that uses starter files, update your local copy before entering the activity directory:

```bash
cd ~/ecpe170-starter-code
git pull --ff-only
```

If Git reports local edits, do not discard them blindly. Preserve your work in your own repository or ask the instructor for help, then update the clean starter copy.

## Available Now

- [`00-healthcheck/`](00-healthcheck/README.md): validate that a personal Linux VM has the complete ECPE 170 toolchain.
- [`01-python-baseline/`](01-python-baseline/README.md): verify, benchmark, profile, and compare the exact Python vector-search reference.
- [`02-cpp-kernel/`](02-cpp-kernel/README.md): build and inspect the portable C++20 distance/search kernel and memory example.
- [`03-python-cpp-extension/`](03-python-cpp-extension/README.md): state the boundary contract, build/import the pybind11 wrapper, compare correctness, and benchmark explicit timing scopes.
- [`04-cache-compiler-parallel/`](04-cache-compiler-parallel/README.md): investigate cache access order, batching/blocking, architecture-native compiler output, serial/parallel search, races, reductions, and false sharing.
- [`05-gpu-fallback-traces/`](05-gpu-fallback-traces/README.md): compare first-class GPU trace, portable-library, and CPU fallback evidence for transfer/compute/total-time reasoning.
- [`06-network-service/`](06-network-service/README.md): test an NDJSON localhost vector-search service, protocol error paths, request logs, and p50/p95/throughput load evidence.
- [`project-cases/`](project-cases/README.md): runnable Performance Emergency Room case packets for the individual Class Project.

## Organization

Use only files that are committed here and linked from the current activity or project brief. The `project-cases/` directory provides working starting systems, but students create their own individual repositories, diagnoses, interventions, and evidence. Private expected outputs, solution sketches, fault maps, troubleshooting notes, and grading anchors belong under `instructor/`, outside this student-facing directory.

## Using Starter Files

1. Copy the relevant starter directory into your personal course repository if the activity asks you to modify it.
2. Preserve the original or commit it before editing so you can inspect your changes.
3. Run the documented correctness checks before collecting performance evidence.
4. Record AI-assisted decisions and verification using the AI Work Log instructions in the course Canvas site when required.
