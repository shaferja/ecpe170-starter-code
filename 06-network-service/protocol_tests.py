#!/usr/bin/env python3
"""Minimal conformance checks for protocol v1."""

from __future__ import annotations

import unittest

from protocol import ProtocolError, decode_request_line, encode_message, make_query_request


class ProtocolConformanceTests(unittest.TestCase):
    def assert_error_code(self, payload: bytes, expected_code: str) -> None:
        with self.assertRaises(ProtocolError) as context:
            decode_request_line(payload)
        self.assertEqual(context.exception.code, expected_code)

    def test_valid_request(self) -> None:
        line = encode_message(make_query_request([1.0, 2.0, 3.0], "valid-1"))
        request = decode_request_line(line)
        self.assertEqual(request["query"], [1.0, 2.0, 3.0])
        self.assertEqual(request["request_id"], "valid-1")

    def test_malformed_json(self) -> None:
        self.assert_error_code(b'{"type":"query"\n', "malformed_json")

    def test_dimension_mismatch(self) -> None:
        self.assert_error_code(
            encode_message(make_query_request([1.0, 2.0], "dim-1")),
            "dimension_mismatch",
        )

    def test_missing_query(self) -> None:
        self.assert_error_code(b'{"type":"query","request_id":"missing-1"}\n', "missing_field")

    def test_unsupported_type(self) -> None:
        self.assert_error_code(b'{"type":"delete","request_id":"type-1"}\n', "unsupported_type")

    def test_missing_newline(self) -> None:
        self.assert_error_code(b'{"type":"query","query":[1,2,3]}', "missing_newline")


if __name__ == "__main__":
    unittest.main(verbosity=2)
