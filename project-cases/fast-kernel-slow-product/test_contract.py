#!/usr/bin/env python3

from __future__ import annotations

import unittest

import numpy as np

import case_b_native
from python_search import find_nearest, make_workload


class ContractTests(unittest.TestCase):
    def test_known_result_matches_all_paths(self) -> None:
        database = [[0.0, 0.0], [1.0, 1.0], [3.0, 3.0]]
        query = [1.1, 0.9]
        expected = find_nearest(database, query)
        copied = case_b_native.find_nearest_copy(database, query)
        self.assertEqual(copied[0], expected[0])
        self.assertAlmostEqual(copied[1], expected[1])
        index = case_b_native.NativeIndex(np.asarray(database, dtype=np.float64))
        reused = index.find(np.asarray(query, dtype=np.float64))
        self.assertEqual(reused[0], expected[0])
        self.assertAlmostEqual(reused[1], expected[1])

    def test_first_minimum_tie_rule(self) -> None:
        database = [[-1.0, 0.0], [1.0, 0.0]]
        query = [0.0, 0.0]
        self.assertEqual(find_nearest(database, query), (0, 1.0))
        self.assertEqual(case_b_native.find_nearest_copy(database, query), (0, 1.0))

    def test_dimension_mismatch(self) -> None:
        index = case_b_native.NativeIndex(np.zeros((2, 3), dtype=np.float64))
        with self.assertRaisesRegex(ValueError, "dimension"):
            index.find(np.zeros(2, dtype=np.float64))

    def test_deterministic_workload(self) -> None:
        self.assertEqual(make_workload(4, 3, 2, 170), make_workload(4, 3, 2, 170))


if __name__ == "__main__":
    unittest.main()
