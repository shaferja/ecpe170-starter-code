#!/usr/bin/env python3
"""NDJSON framing and validation for the ECPE 170 teaching service."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any


EXPECTED_DIMENSION = 3


@dataclass
class ProtocolError(Exception):
    code: str
    message: str
    request_id: str | None = None

    def response(self) -> dict[str, Any]:
        return {
            "ok": False,
            "request_id": self.request_id,
            "error": self.code,
            "message": self.message,
        }


def encode_message(message: dict[str, Any]) -> bytes:
    """Encode exactly one compact JSON object followed by the NDJSON delimiter."""
    return (json.dumps(message, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def decode_request_line(line: bytes, expected_dimension: int = EXPECTED_DIMENSION) -> dict[str, Any]:
    """Decode and validate one complete NDJSON request line."""
    if not line.endswith(b"\n"):
        raise ProtocolError("missing_newline", "request must end with a newline delimiter")
    try:
        text = line[:-1].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProtocolError("invalid_utf8", "request must be UTF-8") from exc
    if not text.strip():
        raise ProtocolError("empty_request", "request line cannot be empty")
    try:
        request = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProtocolError("malformed_json", f"invalid JSON near character {exc.pos}") from exc
    if not isinstance(request, dict):
        raise ProtocolError("invalid_request", "top-level JSON value must be an object")

    raw_request_id = request.get("request_id")
    request_id = raw_request_id if isinstance(raw_request_id, str) else None
    if raw_request_id is not None and request_id is None:
        raise ProtocolError("invalid_request_id", "request_id must be a string", None)

    request_type = request.get("type")
    if request_type is None:
        raise ProtocolError("missing_field", "missing required field: type", request_id)
    if request_type != "query":
        raise ProtocolError("unsupported_type", "only request type 'query' is supported", request_id)

    if "query" not in request:
        raise ProtocolError("missing_field", "missing required field: query", request_id)
    query = request["query"]
    if not isinstance(query, list):
        raise ProtocolError("invalid_query", "query must be a JSON array", request_id)
    if len(query) != expected_dimension:
        raise ProtocolError(
            "dimension_mismatch",
            f"query dimension {len(query)} does not match expected {expected_dimension}",
            request_id,
        )
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in query):
        raise ProtocolError("invalid_query", "query values must be numbers", request_id)
    normalized_query = [float(value) for value in query]
    if any(not math.isfinite(value) for value in normalized_query):
        raise ProtocolError("invalid_query", "query values must be finite", request_id)

    k = request.get("k", 1)
    if k != 1:
        raise ProtocolError("unsupported_k", "protocol v1 supports only k=1", request_id)

    return {
        "type": "query",
        "request_id": request_id,
        "query": normalized_query,
        "k": 1,
    }


def make_query_request(query: list[float], request_id: str) -> dict[str, Any]:
    return {"type": "query", "request_id": request_id, "query": query, "k": 1}
