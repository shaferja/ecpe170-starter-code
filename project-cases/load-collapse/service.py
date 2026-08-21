#!/usr/bin/env python3
"""Deterministic vector-search contract for the load-collapse case."""

from __future__ import annotations

import math
import random
from typing import Any, Sequence


def make_database(count: int = 4000, dimension: int = 32, seed: int = 170) -> tuple[tuple[float, ...], ...]:
    if count <= 0 or dimension <= 0:
        raise ValueError("count and dimension must be positive")
    rng = random.Random(seed)
    return tuple(tuple(rng.uniform(-1.0, 1.0) for _ in range(dimension)) for _ in range(count))


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


def validate_request(value: Any, dimension: int) -> tuple[str, list[float]]:
    if not isinstance(value, dict):
        raise ValueError("request must be a JSON object")
    request_id = value.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request_id must be a non-empty string")
    query = value.get("query")
    if not isinstance(query, list) or len(query) != dimension:
        raise ValueError(f"query must contain exactly {dimension} values")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in query):
        raise ValueError("query values must be numbers")
    normalized = [float(item) for item in query]
    if any(not math.isfinite(item) for item in normalized):
        raise ValueError("query values must be finite")
    return request_id, normalized
