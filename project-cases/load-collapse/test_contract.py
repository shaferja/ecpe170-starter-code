#!/usr/bin/env python3

from __future__ import annotations

import unittest

from service import find_nearest, make_database, squared_distance, validate_request


class ContractTests(unittest.TestCase):
    def test_known_result(self) -> None:
        database = ((0.0, 0.0), (1.0, 1.0), (3.0, 3.0))
        self.assertEqual(find_nearest(database, (1.1, 0.9))[0], 1)

    def test_first_minimum_tie_rule(self) -> None:
        database = ((-1.0, 0.0), (1.0, 0.0))
        self.assertEqual(find_nearest(database, (0.0, 0.0)), (0, 1.0))

    def test_dimension_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "dimension"):
            squared_distance((1.0,), (1.0, 2.0))

    def test_request_validation_and_id(self) -> None:
        request_id, query = validate_request({"request_id": "case-a-1", "query": [1, 2]}, 2)
        self.assertEqual(request_id, "case-a-1")
        self.assertEqual(query, [1.0, 2.0])

    def test_database_is_deterministic(self) -> None:
        self.assertEqual(make_database(3, 2, 170), make_database(3, 2, 170))


if __name__ == "__main__":
    unittest.main()
