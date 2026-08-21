"""Compare the pybind11 extension with the course Python reference contract."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import Callable

import numpy as np

BASELINE_DIR = Path(__file__).resolve().parents[1] / "01-python-baseline"
sys.path.insert(0, str(BASELINE_DIR))

from vector_search_baseline import find_nearest as find_nearest_python  # noqa: E402

import search_ext  # noqa: E402


def compare_case(name: str, vectors: list[list[float]], query: list[float]) -> bool:
    expected = find_nearest_python(vectors, query)
    actual = search_ext.find_nearest(
        np.asarray(vectors, dtype=np.float64, order="C"),
        np.asarray(query, dtype=np.float64, order="C"),
    )
    passed = expected[0] == actual[0] and math.isclose(
        expected[1], actual[1], rel_tol=1e-12, abs_tol=1e-12
    )
    print(
        f"{'PASS' if passed else 'FAIL'} {name}: "
        f"python={expected}, cpp={actual}"
    )
    return passed


def rejects(name: str, operation: Callable[[], object]) -> bool:
    try:
        operation()
    except (TypeError, ValueError) as error:
        print(f"PASS {name}: rejected with {type(error).__name__}: {error}")
        return True
    print(f"FAIL {name}: invalid input was accepted")
    return False


def main() -> None:
    rng = random.Random(170)
    generated = [[rng.random() for _ in range(16)] for _ in range(100)]
    generated_query = [rng.random() for _ in range(16)]

    checks = [
        compare_case("one_vector", [[2.0, -1.0]], [2.0, 1.0]),
        compare_case(
            "known_nearest", [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]], [1.0, 2.0]
        ),
        compare_case("zero_distance", [[0.0, 0.0], [3.0, 4.0]], [3.0, 4.0]),
        compare_case("smallest_index_tie", [[0.0, 0.0], [2.0, 0.0]], [1.0, 0.0]),
        compare_case("generated_100x16", generated, generated_query),
        rejects(
            "empty_vectors",
            lambda: search_ext.find_nearest(
                np.empty((0, 2), dtype=np.float64), np.zeros(2, dtype=np.float64)
            ),
        ),
        rejects(
            "dimension_mismatch",
            lambda: search_ext.find_nearest(
                np.zeros((2, 3), dtype=np.float64), np.zeros(2, dtype=np.float64)
            ),
        ),
        rejects(
            "wrong_dtype",
            lambda: search_ext.find_nearest(
                np.zeros((2, 2), dtype=np.float32), np.zeros(2, dtype=np.float64)
            ),
        ),
        rejects(
            "noncontiguous_vectors",
            lambda: search_ext.find_nearest(
                np.zeros((2, 4), dtype=np.float64)[:, ::2],
                np.zeros(2, dtype=np.float64),
            ),
        ),
    ]
    passed = sum(checks)
    print(f"summary: {passed}/{len(checks)} checks passed")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
