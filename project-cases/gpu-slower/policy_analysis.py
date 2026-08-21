#!/usr/bin/env python3
"""Evaluate CPU/GPU routing policies against the supplied Case C trace."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def choose_path(policy: str, batch_size: int, threshold: int) -> str:
    if policy == "cpu-all":
        return "cpu"
    if policy == "gpu-all":
        return "gpu"
    return "gpu" if batch_size >= threshold else "cpu"


def load_trace(path: Path, residency: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["residency"] == residency]
    if not rows:
        raise ValueError(f"trace has no rows for residency={residency}")
    for row in rows:
        component_total = float(row["h2d_ms"]) + float(row["compute_ms"]) + float(row["d2h_ms"])
        if abs(component_total - float(row["gpu_total_ms"])) > 1e-9:
            raise ValueError(f"component total mismatch in {row['trace_id']}")
        if row["correct"] != "PASS":
            raise ValueError(f"trace correctness failure in {row['trace_id']}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=Path("gpu_trace_packet.csv"))
    parser.add_argument("--policy", choices=("cpu-all", "gpu-all", "hybrid"), required=True)
    parser.add_argument("--threshold", type=positive_int, default=32)
    parser.add_argument("--residency", choices=("database-resident", "copy-each-request"), default="database-resident")
    args = parser.parse_args()

    print("provenance,residency,batch_size,policy,threshold,chosen_path,chosen_total_ms,cpu_total_ms,gpu_total_ms,delta_vs_cpu_ms")
    for row in load_trace(args.trace, args.residency):
        batch = int(row["batch_size"])
        path = choose_path(args.policy, batch, args.threshold)
        cpu_ms = float(row["cpu_total_ms"])
        gpu_ms = float(row["gpu_total_ms"])
        chosen_ms = gpu_ms if path == "gpu" else cpu_ms
        print(
            f"{row['provenance']},{args.residency},{batch},{args.policy},{args.threshold},"
            f"{path},{chosen_ms:.6f},{cpu_ms:.6f},{gpu_ms:.6f},{chosen_ms - cpu_ms:.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
