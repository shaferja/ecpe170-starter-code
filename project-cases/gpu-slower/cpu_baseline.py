#!/usr/bin/env python3
"""Portable CPU evidence generator for Performance Emergency Room Case C."""

from __future__ import annotations

import argparse
import csv
import platform
import random
import statistics
import sys
import time
from pathlib import Path


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def batch_sizes(value: str) -> list[int]:
    try:
        values = [positive_int(item.strip()) for item in value.split(",")]
    except (ValueError, argparse.ArgumentTypeError) as exc:
        raise argparse.ArgumentTypeError("batch sizes must be comma-separated positive integers") from exc
    return values


def make_data(vectors: int, dimension: int, batches: list[int], seed: int) -> tuple[list[list[float]], dict[int, list[list[float]]]]:
    rng = random.Random(seed)
    database = [[rng.uniform(-1.0, 1.0) for _ in range(dimension)] for _ in range(vectors)]
    queries = {batch: [list(database[(index * 37) % vectors]) for index in range(batch)] for batch in batches}
    return database, queries


def find_nearest(database: list[list[float]], query: list[float]) -> tuple[int, float]:
    if not database or len(database[0]) != len(query):
        raise ValueError("database/query dimension mismatch")
    best_index = 0
    best_distance = sum((left - right) ** 2 for left, right in zip(database[0], query))
    for index, vector in enumerate(database[1:], start=1):
        distance = sum((left - right) ** 2 for left, right in zip(vector, query))
        if distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance


def append_rows(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-sizes", type=batch_sizes, default=[1, 8, 32, 128])
    parser.add_argument("--vectors", type=positive_int, default=512)
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--trials", type=positive_int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")

    database, queries = make_data(args.vectors, args.dimension, args.batch_sizes, args.seed)
    fields = ["provenance", "architecture", "python_version", "batch_size", "vectors", "dimension", "median_cpu_total_ms", "median_ms_per_query", "trials", "warmups", "seed", "checksum", "timed_scope", "correct"]
    rows: list[dict[str, object]] = []
    for batch in args.batch_sizes:
        def action() -> list[tuple[int, float]]:
            return [find_nearest(database, query) for query in queries[batch]]

        for _ in range(args.warmups):
            action()
        samples: list[float] = []
        result: list[tuple[int, float]] = []
        for _ in range(args.trials):
            started = time.perf_counter()
            result = action()
            samples.append((time.perf_counter() - started) * 1000.0)
        correct = all(index == (sequence * 37) % args.vectors and abs(distance) <= 1e-12 for sequence, (index, distance) in enumerate(result))
        median_ms = statistics.median(samples)
        rows.append({
            "provenance": "student-measured CPU baseline",
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "batch_size": batch,
            "vectors": args.vectors,
            "dimension": args.dimension,
            "median_cpu_total_ms": f"{median_ms:.9f}",
            "median_ms_per_query": f"{median_ms / batch:.9f}",
            "trials": args.trials,
            "warmups": args.warmups,
            "seed": args.seed,
            "checksum": sum(index for index, _ in result),
            "timed_scope": "CPU search for complete batch; data generation excluded",
            "correct": "PASS" if correct else "FAIL",
        })

    writer = csv.DictWriter(sys.stdout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    if args.csv:
        append_rows(args.csv, fields, rows)
        print(f"csv={args.csv}")
    return 0 if all(row["correct"] == "PASS" for row in rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
