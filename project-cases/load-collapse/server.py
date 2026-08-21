#!/usr/bin/env python3
"""Queue-backed localhost service for Performance Emergency Room Case A."""

from __future__ import annotations

import argparse
import json
import signal
import socket
import socketserver
import threading
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeout
from typing import Any

from service import find_nearest, make_database, validate_request


_LOG_LOCK = threading.Lock()
_WORKER_DATABASE: tuple[tuple[float, ...], ...] | None = None


def log_event(event: dict[str, Any]) -> None:
    with _LOG_LOCK:
        print(json.dumps(event, separators=(",", ":"), sort_keys=True), flush=True)


def initialize_worker(database: tuple[tuple[float, ...], ...]) -> None:
    global _WORKER_DATABASE
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    _WORKER_DATABASE = database


def process_query(query: list[float], enqueued_at: float) -> tuple[int, float, float, float]:
    if _WORKER_DATABASE is None:
        raise RuntimeError("worker database was not initialized")
    started = time.perf_counter()
    best_index, distance = find_nearest(_WORKER_DATABASE, query)
    finished = time.perf_counter()
    return best_index, distance, (started - enqueued_at) * 1000.0, (finished - started) * 1000.0


class WorkDispatcher:
    def __init__(self, database: tuple[tuple[float, ...], ...], worker_count: int, max_queue: int) -> None:
        self.executor = ProcessPoolExecutor(max_workers=worker_count, initializer=initialize_worker, initargs=(database,))
        self.slots = threading.BoundedSemaphore(worker_count + max_queue)
        warmups = [self.executor.submit(process_query, list(database[index % len(database)]), time.perf_counter()) for index in range(worker_count)]
        for future in warmups:
            future.result(timeout=30.0)

    def submit(self, query: list[float], timeout: float) -> tuple[str, tuple[int, float, float, float] | None]:
        if not self.slots.acquire(blocking=False):
            return "queue_full", None
        try:
            future = self.executor.submit(process_query, query, time.perf_counter())
            return "ok", future.result(timeout=timeout)
        except FutureTimeout:
            return "work_timeout", None
        finally:
            self.slots.release()

    def close(self) -> None:
        self.executor.shutdown(wait=True, cancel_futures=True)


class RequestHandler(socketserver.StreamRequestHandler):
    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(self.server.socket_timeout)  # type: ignore[attr-defined]

    def handle(self) -> None:
        request_started = time.perf_counter()
        request_id: str | None = None
        status = "ok"
        error_path: str | None = None
        queue_wait_ms = 0.0
        compute_ms = 0.0
        try:
            line = self.rfile.readline()
            if not line:
                return
            if not line.endswith(b"\n"):
                raise ValueError("request must end with a newline")
            value = json.loads(line)
            request_id, query = validate_request(value, self.server.dimension)  # type: ignore[attr-defined]
            dispatch_status, result = self.server.dispatcher.submit(query, self.server.request_timeout)  # type: ignore[attr-defined]
            if dispatch_status != "ok" or result is None:
                status = "error"
                error_path = dispatch_status
                response = {"ok": False, "request_id": request_id, "error": error_path}
            else:
                best_index, distance, queue_wait_ms, compute_ms = result
                response = {
                    "ok": True,
                    "request_id": request_id,
                    "best_index": best_index,
                    "distance": distance,
                }
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            status = "error"
            error_path = "invalid_request"
            response = {"ok": False, "request_id": request_id, "error": error_path, "message": str(exc)}
        except (TimeoutError, socket.timeout):
            status = "error"
            error_path = "socket_timeout"
            response = {"ok": False, "request_id": request_id, "error": error_path}

        encoded = (json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
        self.wfile.write(encoded)
        self.wfile.flush()
        total_ms = (time.perf_counter() - request_started) * 1000.0
        log_event({
            "event": "request_complete",
            "request_id": request_id,
            "status": status,
            "error_path": error_path,
            "queue_wait_ms": round(queue_wait_ms, 6),
            "compute_ms": round(compute_ms, 6),
            "service_total_ms": round(total_ms, 6),
        })


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 128


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17101)
    parser.add_argument("--workers", type=positive_int, default=2)
    parser.add_argument("--max-queue", type=positive_int, default=64)
    parser.add_argument("--database-size", type=positive_int, default=4000)
    parser.add_argument("--dimension", type=positive_int, default=32)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--socket-timeout", type=float, default=10.0)
    parser.add_argument("--request-timeout", type=float, default=30.0)
    args = parser.parse_args()

    database = make_database(args.database_size, args.dimension, args.seed)
    dispatcher = WorkDispatcher(database, args.workers, args.max_queue)
    try:
        with ThreadedServer((args.host, args.port), RequestHandler) as server:
            server.dimension = args.dimension  # type: ignore[attr-defined]
            server.socket_timeout = args.socket_timeout  # type: ignore[attr-defined]
            server.request_timeout = args.request_timeout  # type: ignore[attr-defined]
            server.dispatcher = dispatcher  # type: ignore[attr-defined]
            log_event({
                "event": "server_listening",
                "host": args.host,
                "port": args.port,
                "workers": args.workers,
                "max_queue": args.max_queue,
                "database_size": args.database_size,
                "dimension": args.dimension,
            })
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                log_event({"event": "server_stopping"})
    finally:
        dispatcher.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
