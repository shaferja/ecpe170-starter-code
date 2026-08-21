#!/usr/bin/env python3
"""Compare Python, conversion-inclusive native, and reusable native-index scopes."""

from __future__ import annotations

import argparse
import csv
import platform
import statistics
import time
from pathlib import Path
from typing import Callable

import numpy as np

import case_b_native
from python_search import find_nearest, make_workload


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def time_scope(action: Callable[[], list[tuple[int, float]]], warmups: int, trials: int) -> tuple[float, list[tuple[int, float]]]:
    result: list[tuple[int, float]] = []
    for _ in range(warmups):
        result = action()
    samples = []
    for _ in range(trials):
        started = time.perf_counter()
        result = action()
        samples.append((time.perf_counter() - started) * 1000.0)
    return statistics.median(samples), result


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
    parser.add_argument("--vectors", nargs="+", type=positive_int, default=[8, 256, 4096])
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=12)
    parser.add_argument("--trials", type=positive_int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")

    fields = ["architecture", "python_version", "vector_count", "dimension", "query_count", "scope", "median_batch_ms", "median_ms_per_query", "trials", "warmups", "seed", "timed_scope", "correct"]
    all_rows: list[dict[str, object]] = []
    for vector_count in args.vectors:
        database, queries = make_workload(vector_count, args.dimension, args.queries, args.seed + vector_count)
        database_array = np.asarray(database, dtype=np.float64, order="C")
        query_arrays = [np.asarray(query, dtype=np.float64, order="C") for query in queries]
        native_index = case_b_native.NativeIndex(database_array)

        actions: list[tuple[str, str, Callable[[], list[tuple[int, float]]]]] = [
            ("python", "Python search calls; database generation excluded", lambda: [find_nearest(database, query) for query in queries]),
            ("native_conversion_inclusive", "per-query Python nested-list to native-vector conversion + native search + result return", lambda: [case_b_native.find_nearest_copy(database, query) for query in queries]),
            ("native_reused_index", "reused native database + preconverted queries + native search + result return; one-time index/query conversion excluded", lambda: [native_index.find(query) for query in query_arrays]),
        ]
        expected = actions[0][2]()
        for scope, timed_scope, action in actions:
            median_ms, result = time_scope(action, args.warmups, args.trials)
            correct = len(result) == len(expected) and all(left[0] == right[0] and abs(left[1] - right[1]) <= 1e-10 for left, right in zip(result, expected))
            all_rows.append({
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "vector_count": vector_count,
                "dimension": args.dimension,
                "query_count": args.queries,
                "scope": scope,
                "median_batch_ms": f"{median_ms:.9f}",
                "median_ms_per_query": f"{median_ms / args.queries:.9f}",
                "trials": args.trials,
                "warmups": args.warmups,
                "seed": args.seed + vector_count,
                "timed_scope": timed_scope,
                "correct": "PASS" if correct else "FAIL",
            })

    writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_rows)
    if args.csv:
        append_rows(args.csv, fields, all_rows)
        print(f"csv={args.csv}")
    return 0 if all(row["correct"] == "PASS" for row in all_rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
