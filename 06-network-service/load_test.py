#!/usr/bin/env python3
"""Concurrent localhost load test with reproducible summary metrics."""

from __future__ import annotations

import argparse
import csv
import math
import platform
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from client import send_query


SUMMARY_FIELDS = [
    "timestamp_utc",
    "architecture",
    "python_version",
    "host",
    "port",
    "clients",
    "request_count",
    "success_count",
    "error_count",
    "elapsed_s",
    "p50_latency_ms",
    "p95_latency_ms",
    "throughput_rps",
    "timed_scope",
]


@dataclass(frozen=True)
class RequestResult:
    request_id: str
    latency_ms: float
    ok: bool
    error: str | None


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def percentile(values: list[float], fraction: float) -> float:
    """Linear interpolation over sorted observations, including both endpoints."""
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def run_request(host: str, port: int, sequence: int, timeout: float) -> RequestResult:
    request_id = f"load-{sequence:06d}"
    query = [1.0 + (sequence % 3) * 0.05, 2.0, 3.0]
    start = time.perf_counter()
    try:
        response = send_query(host, port, query, request_id, timeout)
        latency_ms = (time.perf_counter() - start) * 1000.0
        expected_distance = (query[0] - 1.0) ** 2
        ok = (
            response.get("ok") is True
            and response.get("request_id") == request_id
            and response.get("best_index") == 1
            and isinstance(response.get("distance"), (int, float))
            and math.isclose(float(response["distance"]), expected_distance, rel_tol=1e-12, abs_tol=1e-12)
        )
        error = None if ok else str(response.get("error", "response_mismatch"))
        return RequestResult(request_id, latency_ms, ok, error)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return RequestResult(request_id, latency_ms, False, type(exc).__name__)


def append_summary(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(summary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17000)
    parser.add_argument("--clients", type=positive_int, default=1)
    parser.add_argument("--requests", type=positive_int, default=40, help="total requests")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--csv", type=Path, help="append one aggregate run row to this CSV")
    args = parser.parse_args()

    started = time.perf_counter()
    results: list[RequestResult] = []
    with ThreadPoolExecutor(max_workers=args.clients) as executor:
        futures = [
            executor.submit(run_request, args.host, args.port, sequence, args.timeout)
            for sequence in range(args.requests)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed_s = time.perf_counter() - started

    successes = [result for result in results if result.ok]
    errors = [result for result in results if not result.ok]
    latencies = [result.latency_ms for result in successes]
    p50 = percentile(latencies, 0.50)
    p95 = percentile(latencies, 0.95)
    throughput = len(successes) / elapsed_s if elapsed_s > 0.0 else 0.0
    timed_scope = "client connect+send, localhost service, receive+response parse; excludes server startup"

    print(f"clients={args.clients}")
    print(f"request_count={len(results)}")
    print(f"success_count={len(successes)}")
    print(f"error_count={len(errors)}")
    print(f"elapsed_s={elapsed_s:.6f}")
    print(f"p50_latency_ms={p50:.6f}")
    print(f"p95_latency_ms={p95:.6f}")
    print(f"throughput_rps={throughput:.3f}")
    print(f"timed_scope={timed_scope}")
    if errors:
        counts: dict[str, int] = {}
        for result in errors:
            key = result.error or "unknown"
            counts[key] = counts.get(key, 0) + 1
        print("errors=" + ",".join(f"{key}:{value}" for key, value in sorted(counts.items())))

    if args.csv:
        summary = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "host": args.host,
            "port": args.port,
            "clients": args.clients,
            "request_count": len(results),
            "success_count": len(successes),
            "error_count": len(errors),
            "elapsed_s": f"{elapsed_s:.9f}",
            "p50_latency_ms": f"{p50:.9f}",
            "p95_latency_ms": f"{p95:.9f}",
            "throughput_rps": f"{throughput:.9f}",
            "timed_scope": timed_scope,
        }
        append_summary(args.csv, summary)
        print(f"csv={args.csv}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
