"""Reproducible benchmark harness for exact pure-Python vector search."""

from __future__ import annotations

import argparse
import csv
import platform
import random
import statistics
import sys
import time
from collections.abc import Callable, Sequence

from vector_search_baseline import find_nearest, find_nearest_flat

SearchFunction = Callable[[Sequence[float]], tuple[int, float]]


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
    parser.add_argument("--vectors", type=positive_int, default=2_000,
                        help="number of stored vectors (the input size)")
    parser.add_argument("--dimension", "--dim", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=10)
    parser.add_argument("--trials", type=positive_int, default=7)
    parser.add_argument("--warmups", type=nonnegative_int, default=2)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--representation", choices=("nested", "flat"),
                        default="nested")
    parser.add_argument("--format", "--output-format", dest="output_format",
                        choices=("table", "csv"), default="table")
    return parser.parse_args()


def make_inputs(
    vector_count: int, dimension: int, query_count: int, seed: int
) -> tuple[list[list[float]], list[list[float]]]:
    rng = random.Random(seed)
    vectors = [
        [rng.random() for _ in range(dimension)] for _ in range(vector_count)
    ]
    queries = [
        [rng.random() for _ in range(dimension)] for _ in range(query_count)
    ]
    return vectors, queries


def make_search(
    vectors: list[list[float]], dimension: int, representation: str
) -> SearchFunction:
    if representation == "nested":
        return lambda query: find_nearest(vectors, query)

    flat_vectors = [value for vector in vectors for value in vector]
    return lambda query: find_nearest_flat(flat_vectors, query, dimension)


def time_queries(
    search: SearchFunction, queries: list[list[float]]
) -> tuple[float, tuple[int, float]]:
    start = time.perf_counter()
    index_checksum = 0
    distance_checksum = 0.0
    for query in queries:
        index, distance = search(query)
        index_checksum += index
        distance_checksum += distance
    elapsed = time.perf_counter() - start
    return elapsed, (index_checksum, distance_checksum)


def benchmark(args: argparse.Namespace) -> dict[str, object]:
    # Data generation and representation conversion happen before the timer.
    vectors, queries = make_inputs(
        args.vectors, args.dimension, args.queries, args.seed
    )
    search = make_search(vectors, args.dimension, args.representation)

    for _ in range(args.warmups):
        time_queries(search, queries)

    times: list[float] = []
    expected_checksum: tuple[int, float] | None = None
    for _ in range(args.trials):
        elapsed, checksum = time_queries(search, queries)
        if expected_checksum is None:
            expected_checksum = checksum
        elif checksum != expected_checksum:
            raise RuntimeError("search result changed between trials")
        times.append(elapsed)

    assert expected_checksum is not None
    return {
        "vectors": args.vectors,
        "dimension": args.dimension,
        "queries": args.queries,
        "trials": args.trials,
        "warmups": args.warmups,
        "seed": args.seed,
        "representation": args.representation,
        "timed_scope": "exact search for all queries; setup/conversion excluded",
        "min_s": min(times),
        "median_s": statistics.median(times),
        "max_s": max(times),
        "median_ms_per_query": statistics.median(times) * 1_000 / args.queries,
        "index_checksum": expected_checksum[0],
        "distance_checksum": expected_checksum[1],
        "python": sys.version.split()[0],
        "architecture": platform.machine() or "unknown",
        "platform": platform.platform(),
    }


def print_table(result: dict[str, object]) -> None:
    print("ECPE 170 vector-search benchmark")
    for key in (
        "vectors", "dimension", "queries", "trials", "warmups", "seed",
        "representation", "timed_scope", "python", "architecture", "platform",
    ):
        print(f"{key}: {result[key]}")
    print()
    print("summary")
    print(f"min_s: {result['min_s']:.9f}")
    print(f"median_s: {result['median_s']:.9f}")
    print(f"max_s: {result['max_s']:.9f}")
    print(f"median_ms_per_query: {result['median_ms_per_query']:.6f}")
    print(f"index_checksum: {result['index_checksum']}")
    print(f"distance_checksum: {result['distance_checksum']:.12f}")


def print_csv(result: dict[str, object]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=result.keys())
    writer.writeheader()
    writer.writerow(result)


def main() -> None:
    args = parse_args()
    result = benchmark(args)
    if args.output_format == "csv":
        print_csv(result)
    else:
        print_table(result)


if __name__ == "__main__":
    main()
