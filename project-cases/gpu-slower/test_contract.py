#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path

from cpu_baseline import find_nearest, make_data
from policy_analysis import choose_path, load_trace


class ContractTests(unittest.TestCase):
    def test_cpu_known_result_and_tie(self) -> None:
        self.assertEqual(find_nearest([[0.0], [2.0]], [1.0]), (0, 1.0))

    def test_cpu_dimension_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "dimension"):
            find_nearest([[0.0, 1.0]], [0.0])

    def test_deterministic_data(self) -> None:
        self.assertEqual(make_data(4, 2, [1, 2], 170), make_data(4, 2, [1, 2], 170))

    def test_trace_component_totals_and_correctness(self) -> None:
        path = Path(__file__).with_name("gpu_trace_packet.csv")
        self.assertEqual(len(load_trace(path, "database-resident")), 4)
        self.assertEqual(len(load_trace(path, "copy-each-request")), 4)

    def test_hybrid_policy_boundary(self) -> None:
        self.assertEqual(choose_path("hybrid", 8, 32), "cpu")
        self.assertEqual(choose_path("hybrid", 32, 32), "gpu")


if __name__ == "__main__":
    unittest.main()
