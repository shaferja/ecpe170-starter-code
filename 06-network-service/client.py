#!/usr/bin/env python3
"""Client for valid and deliberately malformed NDJSON teaching requests."""

from __future__ import annotations

import argparse
import json
import socket
import uuid
from typing import Any

from protocol import encode_message, make_query_request


def parse_query(value: str) -> list[float]:
    try:
        query = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("query must contain comma-separated numbers") from exc
    if not query:
        raise argparse.ArgumentTypeError("query cannot be empty")
    return query


def exchange(host: str, port: int, payload: bytes, timeout: float = 5.0) -> dict[str, Any]:
    """Connect, send one framed request, and parse one framed response."""
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.sendall(payload)
        with connection.makefile("rb") as response_stream:
            response_line = response_stream.readline()
    if not response_line:
        raise RuntimeError("server closed without a response line")
    if not response_line.endswith(b"\n"):
        raise RuntimeError("server response is missing the newline delimiter")
    response = json.loads(response_line)
    if not isinstance(response, dict):
        raise RuntimeError("server response must be a JSON object")
    return response


def send_query(
    host: str,
    port: int,
    query: list[float],
    request_id: str,
    timeout: float = 5.0,
) -> dict[str, Any]:
    return exchange(host, port, encode_message(make_query_request(query, request_id)), timeout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17000)
    parser.add_argument("--request-id", default=f"client-{uuid.uuid4().hex[:8]}")
    request_group = parser.add_mutually_exclusive_group(required=True)
    request_group.add_argument("--query", type=parse_query)
    request_group.add_argument("--raw", help="send this text as one newline-framed payload")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    if args.raw is not None:
        payload = args.raw.encode("utf-8") + b"\n"
    else:
        payload = encode_message(make_query_request(args.query, args.request_id))
    response = exchange(args.host, args.port, payload, args.timeout)
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0 if response.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
