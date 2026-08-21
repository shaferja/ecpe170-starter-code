#!/usr/bin/env python3
"""Small dependency-free measurement helpers shared by project cases."""

from __future__ import annotations

import csv
import math
import platform
from pathlib import Path
from typing import Iterable, Mapping


def percentile(values: Iterable[float], fraction: float) -> float:
    observations = sorted(float(value) for value in values)
    if not observations:
        return math.nan
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    position = (len(observations) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return observations[lower]
    weight = position - lower
    return observations[lower] * (1.0 - weight) + observations[upper] * weight


def environment() -> dict[str, str]:
    return {
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def append_csv(path: Path, fields: list[str], row: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in fields})
