"""Benchmark pure Python and pybind11 search with explicit timing scopes."""

from __future__ import annotations

import argparse
import csv
import platform
import random
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np

BASELINE_DIR = Path(__file__).resolve().parents[1] / "01-python-baseline"
sys.path.insert(0, str(BASELINE_DIR))

from vector_search_baseline import find_nearest as find_nearest_python  # noqa: E402

import search_ext  # noqa: E402

SearchBatch = Callable[[], tuple[int, float]]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be at least 0")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors", type=positive_int, nargs="+", default=[1, 32, 512, 5000])
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=10)
    parser.add_argument("--trials", type=positive_int, default=7)
    parser.add_argument("--warmups", type=nonnegative_int, default=2)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--format", choices=("table", "csv"), default="table")
    return parser.parse_args()


def make_inputs(
    vector_count: int, dimension: int, query_count: int, seed: int
) -> tuple[list[list[float]], list[list[float]]]:
    rng = random.Random(seed)
    vectors = [[rng.random() for _ in range(dimension)] for _ in range(vector_count)]
    queries = [[rng.random() for _ in range(dimension)] for _ in range(query_count)]
    return vectors, queries


def checksum(results: list[tuple[int, float]]) -> tuple[int, float]:
    return sum(item[0] for item in results), sum(item[1] for item in results)


def time_batch(operation: SearchBatch) -> tuple[float, tuple[int, float]]:
    start = time.perf_counter()
    result = operation()
    return time.perf_counter() - start, result


def measure(operation: SearchBatch, trials: int, warmups: int) -> tuple[float, tuple[int, float]]:
    for _ in range(warmups):
        operation()

    samples: list[float] = []
    expected: tuple[int, float] | None = None
    for _ in range(trials):
        elapsed, result = time_batch(operation)
        if expected is None:
            expected = result
        elif result[0] != expected[0] or not np.isclose(result[1], expected[1], rtol=1e-12, atol=1e-12):
            raise RuntimeError("search checksum changed between trials")
        samples.append(elapsed)
    assert expected is not None
    return statistics.median(samples), expected


def benchmark_size(args: argparse.Namespace, vector_count: int) -> list[dict[str, object]]:
    vectors, queries = make_inputs(vector_count, args.dimension, args.queries, args.seed)
    vectors_np = np.asarray(vectors, dtype=np.float64, order="C")
    queries_np = np.asarray(queries, dtype=np.float64, order="C")

    def python_batch() -> tuple[int, float]:
        return checksum([find_nearest_python(vectors, query) for query in queries])

    def native_preconverted_batch() -> tuple[int, float]:
        return checksum([search_ext.find_nearest(vectors_np, query) for query in queries_np])

    def native_conversion_inclusive_batch() -> tuple[int, float]:
        timed_vectors = np.asarray(vectors, dtype=np.float64, order="C")
        timed_queries = np.asarray(queries, dtype=np.float64, order="C")
        return checksum(
            [search_ext.find_nearest(timed_vectors, query) for query in timed_queries]
        )

    operations = [
        (
            "python",
            "exact search for all queries; input generation excluded",
            python_batch,
        ),
        (
            "native_preconverted",
            "pybind calls plus native search; NumPy conversion excluded",
            native_preconverted_batch,
        ),
        (
            "native_conversion_inclusive",
            "NumPy conversion plus pybind calls plus native search",
            native_conversion_inclusive_batch,
        ),
    ]

    rows: list[dict[str, object]] = []
    expected: tuple[int, float] | None = None
    for path, timed_scope, operation in operations:
        median_s, result = measure(operation, args.trials, args.warmups)
        if expected is None:
            expected = result
        elif result[0] != expected[0] or not np.isclose(result[1], expected[1], rtol=1e-12, atol=1e-12):
            raise RuntimeError(f"{path} does not match the Python result")
        rows.append(
            {
                "path": path,
                "vectors": vector_count,
                "dimension": args.dimension,
                "queries": args.queries,
                "trials": args.trials,
                "warmups": args.warmups,
                "seed": args.seed,
                "timed_scope": timed_scope,
                "median_s": median_s,
                "median_ms_per_query": median_s * 1000 / args.queries,
                "index_checksum": result[0],
                "distance_checksum": f"{result[1]:.12f}",
                "python": platform.python_version(),
                "architecture": platform.machine() or "unknown",
            }
        )
    return rows


def print_table(rows: list[dict[str, object]]) -> None:
    print("ECPE 170 Python/C++ boundary benchmark")
    print(f"python={platform.python_version()} architecture={platform.machine() or 'unknown'}")
    print("times vary by machine; compare correctness and trends, not exact values")
    print()
    print(f"{'vectors':>8}  {'path':<29} {'median ms/query':>16}  timed scope")
    for row in rows:
        print(
            f"{row['vectors']:>8}  {row['path']:<29} "
            f"{row['median_ms_per_query']:>16.6f}  {row['timed_scope']}"
        )


def main() -> None:
    args = parse_args()
    rows = [row for size in args.vectors for row in benchmark_size(args, size)]
    if args.format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        print_table(rows)


if __name__ == "__main__":
    main()
