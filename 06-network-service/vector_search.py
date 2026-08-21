#!/usr/bin/env python3
"""Small deterministic exact vector-search kernel used by the service starter."""

from __future__ import annotations

from typing import Sequence


VECTORS: tuple[tuple[float, ...], ...] = (
    (0.0, 0.0, 0.0),
    (1.0, 2.0, 3.0),
    (2.0, 2.0, 2.0),
    (-1.0, 0.0, 1.0),
    (4.0, 4.0, 4.0),
)


def squared_distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("dimension mismatch inside vector kernel")
    return sum((a - b) * (a - b) for a, b in zip(left, right))


def find_nearest(query: Sequence[float]) -> tuple[int, float]:
    """Return the first minimum index and squared distance for the fixed dataset."""
    best_index = 0
    best_distance = squared_distance(VECTORS[0], query)
    for index in range(1, len(VECTORS)):
        distance = squared_distance(VECTORS[index], query)
        if distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance
