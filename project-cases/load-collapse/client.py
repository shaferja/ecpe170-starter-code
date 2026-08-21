#!/usr/bin/env python3
"""One-request NDJSON client for the load-collapse case."""

from __future__ import annotations

import json
import socket
from typing import Any


def send_request(host: str, port: int, request: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
    payload = (json.dumps(request, separators=(",", ":")) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.sendall(payload)
        stream = connection.makefile("rb")
        line = stream.readline()
    if not line:
        raise RuntimeError("server closed without a response")
    response = json.loads(line)
    if not isinstance(response, dict):
        raise RuntimeError("response must be a JSON object")
    return response
