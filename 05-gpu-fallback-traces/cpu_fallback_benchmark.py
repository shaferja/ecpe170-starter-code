#!/usr/bin/env python3
"""Portable CPU evidence with the same table shape as the GPU trace packet."""

from __future__ import annotations

import argparse
import csv
import platform
import random
import statistics
import time
from pathlib import Path
from typing import Iterable


FIELDNAMES = [
    "evidence_path",
    "batch_size",
    "data_residency",
    "h2d_ms",
    "launch_compute_ms",
    "d2h_ms",
    "total_ms",
    "notes",
]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def parse_batch_sizes(value: str) -> list[int]:
    try:
        sizes = [positive_int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("batch sizes must be comma-separated integers") from exc
    if not sizes:
        raise argparse.ArgumentTypeError("provide at least one batch size")
    return sizes


def make_matrix(rows: int, dimension: int, rng: random.Random) -> list[list[float]]:
    return [[rng.uniform(-1.0, 1.0) for _ in range(dimension)] for _ in range(rows)]


def squared_distance(left: Iterable[float], right: Iterable[float]) -> float:
    return sum((a - b) * (a - b) for a, b in zip(left, right))


def find_nearest(vectors: list[list[float]], query: list[float]) -> tuple[int, float]:
    best_index = 0
    best_distance = squared_distance(vectors[0], query)
    for index in range(1, len(vectors)):
        distance = squared_distance(vectors[index], query)
        if distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance


def median_ms(samples: list[float]) -> float:
    return statistics.median(samples) * 1000.0


def measure_batch(
    vectors: list[list[float]],
    source_queries: list[list[float]],
    trials: int,
    residency: str,
) -> dict[str, object]:
    input_times: list[float] = []
    compute_times: list[float] = []
    result_times: list[float] = []
    total_times: list[float] = []
    checksum: int | None = None

    for _ in range(trials):
        total_start = time.perf_counter()

        input_start = time.perf_counter()
        working_vectors = [row[:] for row in vectors] if residency == "copy_each_trial" else vectors
        working_queries = [row[:] for row in source_queries]
        input_end = time.perf_counter()

        compute_start = time.perf_counter()
        working_results = [find_nearest(working_vectors, query) for query in working_queries]
        compute_end = time.perf_counter()

        result_start = time.perf_counter()
        host_results = list(working_results)
        result_end = time.perf_counter()

        observed_checksum = sum(index for index, _ in host_results)
        if checksum is None:
            checksum = observed_checksum
        elif observed_checksum != checksum:
            raise RuntimeError("correctness receipt changed across identical trials")

        input_times.append(input_end - input_start)
        compute_times.append(compute_end - compute_start)
        result_times.append(result_end - result_start)
        total_times.append(result_end - total_start)

    return {
        "evidence_path": "cpu_fallback_analogs",
        "batch_size": len(source_queries),
        "data_residency": residency,
        "h2d_ms": median_ms(input_times),
        "launch_compute_ms": median_ms(compute_times),
        "d2h_ms": median_ms(result_times),
        "total_ms": median_ms(total_times),
        "notes": f"CPU analog fields; checksum={checksum}",
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            for field in ("h2d_ms", "launch_compute_ms", "d2h_ms", "total_ms"):
                formatted[field] = f"{float(row[field]):.6f}"
            writer.writerow(formatted)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-sizes", type=parse_batch_sizes, default=parse_batch_sizes("1,8,32"))
    parser.add_argument("--vectors", type=positive_int, default=256)
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--trials", type=positive_int, default=3)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument(
        "--database-residency",
        choices=("resident", "copy_each_trial"),
        default="resident",
    )
    parser.add_argument("--csv", type=Path, help="write the timing rows to this CSV file")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    vectors = make_matrix(args.vectors, args.dimension, rng)
    queries = make_matrix(max(args.batch_sizes), args.dimension, rng)
    rows = [
        measure_batch(vectors, queries[:batch_size], args.trials, args.database_residency)
        for batch_size in args.batch_sizes
    ]

    print(f"architecture={platform.machine()} vectors={args.vectors} dimension={args.dimension} trials={args.trials}")
    print("timed_scope=CPU input-copy analog + exact CPU compute + result-copy analog")
    print("batch_size,h2d_ms,launch_compute_ms,d2h_ms,total_ms,checksum_note")
    for row in rows:
        print(
            f"{row['batch_size']},{row['h2d_ms']:.6f},{row['launch_compute_ms']:.6f},"
            f"{row['d2h_ms']:.6f},{row['total_ms']:.6f},{row['notes']}"
        )

    if args.csv:
        write_csv(args.csv, rows)
        print(f"csv={args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
