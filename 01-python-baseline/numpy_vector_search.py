"""Correctness and timing comparison for Python and NumPy exact search."""

from __future__ import annotations

import argparse
import math
import statistics
import time

try:
    import numpy as np
except ImportError as error:  # Give a focused message instead of a long traceback.
    raise SystemExit("NumPy is required: install the course VM tool set first") from error

from vector_search_baseline import find_nearest
from vector_search_benchmark import make_inputs, nonnegative_int, positive_int


def find_nearest_numpy(vectors_array: np.ndarray, query_array: np.ndarray) -> tuple[int, float]:
    """Search existing float64 NumPy arrays; no input conversion happens here."""
    if vectors_array.ndim != 2 or vectors_array.shape[0] == 0:
        raise ValueError("vectors must be a non-empty two-dimensional array")
    if query_array.ndim != 1 or query_array.shape[0] != vectors_array.shape[1]:
        raise ValueError("vector and query dimensions must match")
    if vectors_array.shape[1] == 0:
        raise ValueError("vectors must have at least one dimension")

    differences = vectors_array - query_array
    distances = np.sum(differences * differences, axis=1)
    best_index = int(np.argmin(distances))
    return best_index, float(distances[best_index])


def find_nearest_numpy_with_conversion(vectors, query) -> tuple[int, float]:
    """Convert Python lists on each call, then search the resulting arrays."""
    vectors_array = np.asarray(vectors, dtype=np.float64)
    query_array = np.asarray(query, dtype=np.float64)
    return find_nearest_numpy(vectors_array, query_array)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors", type=positive_int, default=5_000)
    parser.add_argument("--dimension", "--dim", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=10)
    parser.add_argument("--trials", type=positive_int, default=7)
    parser.add_argument("--warmups", type=nonnegative_int, default=2)
    parser.add_argument("--seed", type=int, default=170)
    return parser.parse_args()


def time_call(function, trials: int, warmups: int) -> list[float]:
    for _ in range(warmups):
        function()
    times = []
    for _ in range(trials):
        start = time.perf_counter()
        function()
        times.append(time.perf_counter() - start)
    return times


def main() -> None:
    args = parse_args()
    vectors, queries = make_inputs(
        args.vectors, args.dimension, args.queries, args.seed
    )
    # Convert once before timing the numpy_preconverted workload.
    vectors_array = np.asarray(vectors, dtype=np.float64)
    queries_array = np.asarray(queries, dtype=np.float64)

    expected = [find_nearest(vectors, query) for query in queries]
    actual = [find_nearest_numpy(vectors_array, query) for query in queries_array]
    for expected_result, actual_result in zip(expected, actual):
        same_index = expected_result[0] == actual_result[0]
        same_distance = math.isclose(
            expected_result[1], actual_result[1], rel_tol=1e-12, abs_tol=1e-12
        )
        if not (same_index and same_distance):
            raise RuntimeError("NumPy and Python results differ; stop before timing")

    workloads = {
        "python_nested": lambda: [find_nearest(vectors, query) for query in queries],
        "numpy_conversion_included": lambda: [
            find_nearest_numpy_with_conversion(vectors, query) for query in queries
        ],
        "numpy_preconverted": lambda: [
            find_nearest_numpy(vectors_array, query) for query in queries_array
        ],
    }

    print("version,timed_scope,median_s,min_s,max_s")
    for name, workload in workloads.items():
        times = time_call(workload, args.trials, args.warmups)
        scope = (
            "search plus repeated array conversion"
            if name == "numpy_conversion_included"
            else "search only; input setup excluded"
        )
        print(
            f'{name},"{scope}",{statistics.median(times):.9f},'
            f"{min(times):.9f},{max(times):.9f}"
        )


if __name__ == "__main__":
    main()
