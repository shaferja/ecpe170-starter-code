#!/usr/bin/env python3
"""Concurrent client workload and evidence receipt for Case A."""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from measurement import append_csv, environment, percentile  # noqa: E402

from client import send_request
from service import make_database


FIELDS = [
    "architecture", "python_version", "host", "port", "clients", "request_count",
    "success_count", "error_count", "elapsed_s", "p50_latency_ms", "p95_latency_ms",
    "throughput_rps", "database_size", "dimension", "seed", "timed_scope",
]


@dataclass(frozen=True)
class Result:
    latency_ms: float
    ok: bool
    error: str | None


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def run_one(host: str, port: int, sequence: int, query: list[float], expected_index: int, timeout: float) -> Result:
    request_id = f"case-a-{sequence:06d}"
    started = time.perf_counter()
    try:
        response = send_request(host, port, {"request_id": request_id, "query": query}, timeout)
        latency_ms = (time.perf_counter() - started) * 1000.0
        ok = response.get("ok") is True and response.get("request_id") == request_id and response.get("best_index") == expected_index
        return Result(latency_ms, ok, None if ok else str(response.get("error", "response_mismatch")))
    except Exception as exc:
        return Result((time.perf_counter() - started) * 1000.0, False, type(exc).__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17101)
    parser.add_argument("--clients", type=positive_int, default=1)
    parser.add_argument("--requests", type=positive_int, default=24)
    parser.add_argument("--database-size", type=positive_int, default=4000)
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    database = make_database(args.database_size, args.dimension, args.seed)
    work = []
    for sequence in range(args.requests):
        expected_index = (sequence * 37) % len(database)
        work.append((sequence, list(database[expected_index]), expected_index))

    started = time.perf_counter()
    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=args.clients) as executor:
        futures = [executor.submit(run_one, args.host, args.port, sequence, query, expected, args.timeout) for sequence, query, expected in work]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed_s = time.perf_counter() - started

    successful = [result for result in results if result.ok]
    errors = [result for result in results if not result.ok]
    latencies = [result.latency_ms for result in successful]
    env = environment()
    row: dict[str, object] = {
        "architecture": env["architecture"],
        "python_version": env["python_version"],
        "host": args.host,
        "port": args.port,
        "clients": args.clients,
        "request_count": len(results),
        "success_count": len(successful),
        "error_count": len(errors),
        "elapsed_s": f"{elapsed_s:.9f}",
        "p50_latency_ms": f"{percentile(latencies, 0.50):.9f}",
        "p95_latency_ms": f"{percentile(latencies, 0.95):.9f}",
        "throughput_rps": f"{len(successful) / elapsed_s:.9f}",
        "database_size": args.database_size,
        "dimension": args.dimension,
        "seed": args.seed,
        "timed_scope": "client connect+send, server queue+compute+response, receive+validate; excludes server/database startup",
    }
    for field in FIELDS:
        print(f"{field}={row[field]}")
    if errors:
        counts: dict[str, int] = {}
        for result in errors:
            key = result.error or "unknown"
            counts[key] = counts.get(key, 0) + 1
        print("errors=" + ",".join(f"{name}:{count}" for name, count in sorted(counts.items())))
    if args.csv:
        append_csv(args.csv, FIELDS, row)
        print(f"csv={args.csv}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
