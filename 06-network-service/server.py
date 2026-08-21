#!/usr/bin/env python3
"""Local NDJSON vector-search server with lightweight timing receipts."""

from __future__ import annotations

import argparse
import json
import socket
import socketserver
import threading
import time
from typing import Any

from protocol import ProtocolError, decode_request_line, encode_message
from vector_search import find_nearest


_LOG_LOCK = threading.Lock()


def log_event(event: dict[str, Any]) -> None:
    with _LOG_LOCK:
        print(json.dumps(event, separators=(",", ":"), sort_keys=True), flush=True)


class RequestHandler(socketserver.StreamRequestHandler):
    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(self.server.socket_timeout)  # type: ignore[attr-defined]

    def handle(self) -> None:
        peer = f"{self.client_address[0]}:{self.client_address[1]}"
        while True:
            read_start = time.perf_counter()
            try:
                line = self.rfile.readline()
            except (TimeoutError, socket.timeout):
                log_event({"event": "connection_timeout", "peer": peer, "error_path": "blocked_read"})
                return
            if not line:
                return

            request_id: str | None = None
            parse_ms = 0.0
            compute_ms = 0.0
            status = "ok"
            error_path: str | None = None
            if self.server.trace:  # type: ignore[attr-defined]
                log_event({"event": "frame_received", "peer": peer, "bytes_in": len(line)})

            try:
                parse_start = time.perf_counter()
                request = decode_request_line(line)
                parse_ms = (time.perf_counter() - parse_start) * 1000.0
                request_id = request["request_id"]
                if self.server.trace:  # type: ignore[attr-defined]
                    log_event({"event": "request_validated", "request_id": request_id, "peer": peer})

                compute_start = time.perf_counter()
                best_index, distance = find_nearest(request["query"])
                compute_ms = (time.perf_counter() - compute_start) * 1000.0
                response = {
                    "ok": True,
                    "request_id": request_id,
                    "best_index": best_index,
                    "distance": distance,
                }
            except ProtocolError as exc:
                parse_ms = (time.perf_counter() - parse_start) * 1000.0
                request_id = exc.request_id
                status = "error"
                error_path = exc.code
                response = exc.response()
            except Exception as exc:  # keep the teaching server alive and expose the layer
                status = "error"
                error_path = "compute_error"
                response = {
                    "ok": False,
                    "request_id": request_id,
                    "error": "compute_error",
                    "message": str(exc),
                }

            response_bytes = encode_message(response)
            self.wfile.write(response_bytes)
            self.wfile.flush()
            response_ms = (time.perf_counter() - read_start) * 1000.0
            log_event(
                {
                    "event": "request_complete",
                    "request_id": request_id,
                    "peer": peer,
                    "status": status,
                    "error_path": error_path,
                    "bytes_in": len(line),
                    "bytes_out": len(response_bytes),
                    "parse_ms": round(parse_ms, 6),
                    "compute_ms": round(compute_ms, 6),
                    "response_ms": round(response_ms, 6),
                }
            )


class SerialServer(socketserver.TCPServer):
    allow_reuse_address = True


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17000)
    parser.add_argument("--mode", choices=("serial", "threaded"), default="serial")
    parser.add_argument("--trace", action="store_true", help="print framing/validation stage events")
    parser.add_argument("--socket-timeout", type=float, default=5.0)
    args = parser.parse_args()

    server_class = SerialServer if args.mode == "serial" else ThreadedServer
    with server_class((args.host, args.port), RequestHandler) as server:
        server.trace = args.trace  # type: ignore[attr-defined]
        server.socket_timeout = args.socket_timeout  # type: ignore[attr-defined]
        log_event(
            {
                "event": "server_listening",
                "host": args.host,
                "port": args.port,
                "mode": args.mode,
                "protocol": "ndjson-v1",
            }
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log_event({"event": "server_stopping"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
