#!/usr/bin/env python3
"""Reference search and deterministic workloads for Case B."""

from __future__ import annotations

import random
from typing import Sequence


def make_workload(vector_count: int, dimension: int, query_count: int, seed: int) -> tuple[list[list[float]], list[list[float]]]:
    if vector_count <= 0 or dimension <= 0 or query_count <= 0:
        raise ValueError("workload sizes must be positive")
    rng = random.Random(seed)
    database = [[rng.uniform(-1.0, 1.0) for _ in range(dimension)] for _ in range(vector_count)]
    queries = [list(database[(index * 37) % vector_count]) for index in range(query_count)]
    return database, queries


def squared_distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum((a - b) * (a - b) for a, b in zip(left, right))


def find_nearest(database: Sequence[Sequence[float]], query: Sequence[float]) -> tuple[int, float]:
    if not database:
        raise ValueError("database must be non-empty")
    best_index = 0
    best_distance = squared_distance(database[0], query)
    for index in range(1, len(database)):
        distance = squared_distance(database[index], query)
        if distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance
