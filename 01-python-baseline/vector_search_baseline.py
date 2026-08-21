"""Readable exact vector-search baselines used in ECPE 170.

The functions favor an explicit contract and easy inspection over cleverness. Later
course versions must match these answers before their performance is compared.
"""

from __future__ import annotations

from collections.abc import Sequence


def squared_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """Return squared Euclidean distance between equal-length, non-empty vectors."""
    if len(a) != len(b):
        raise ValueError("vector and query dimensions must match")
    if not a:
        raise ValueError("vectors must have at least one dimension")

    total = 0.0
    for left, right in zip(a, b):
        difference = left - right
        total += difference * difference
    return total


def find_nearest(
    vectors: Sequence[Sequence[float]], query: Sequence[float]
) -> tuple[int, float]:
    """Return ``(smallest best index, squared distance)`` for an exact search."""
    if not vectors:
        raise ValueError("vectors must be non-empty")

    best_index = 0
    best_distance = squared_distance(vectors[0], query)

    for index in range(1, len(vectors)):
        distance = squared_distance(vectors[index], query)
        # Strictly less preserves the required first-match (smallest-index) tie rule.
        if distance < best_distance:
            best_index = index
            best_distance = distance

    return best_index, best_distance


def find_nearest_flat(
    flat_vectors: Sequence[float], query: Sequence[float], dimension: int
) -> tuple[int, float]:
    """Search vectors stored consecutively in one flat Python sequence."""
    if dimension < 1:
        raise ValueError("dimension must be at least 1")
    if len(query) != dimension:
        raise ValueError("vector and query dimensions must match")
    if not flat_vectors:
        raise ValueError("vectors must be non-empty")
    if len(flat_vectors) % dimension != 0:
        raise ValueError("flat vector data length must be divisible by dimension")

    best_index = 0
    best_distance = float("inf")
    vector_count = len(flat_vectors) // dimension

    for vector_index in range(vector_count):
        start = vector_index * dimension
        distance = 0.0
        for coordinate in range(dimension):
            difference = flat_vectors[start + coordinate] - query[coordinate]
            distance += difference * difference
        if distance < best_distance:
            best_index = vector_index
            best_distance = distance

    return best_index, best_distance


if __name__ == "__main__":
    example_vectors = [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]]
    example_query = [1.0, 2.0]
    print(find_nearest(example_vectors, example_query))
