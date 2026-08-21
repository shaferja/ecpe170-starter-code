"""Correctness contract for the ECPE 170 Python vector-search baseline."""

import unittest

from vector_search_baseline import find_nearest, find_nearest_flat


class VectorSearchContractTests(unittest.TestCase):
    def test_one_vector_input(self):
        self.assertEqual(find_nearest([[2.0, 3.0]], [5.0, 7.0]), (0, 25.0))

    def test_known_nearest_vector(self):
        vectors = [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 2.0]), (2, 1.0))

    def test_zero_distance(self):
        vectors = [[5.0, 5.0], [1.0, 2.0], [9.0, 9.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 2.0]), (1, 0.0))

    def test_tie_returns_smallest_index(self):
        vectors = [[0.0, 0.0], [2.0, 0.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 0.0]), (0, 1.0))

    def test_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, "dimensions must match"):
            find_nearest([[0.0, 1.0], [2.0]], [0.0, 1.0])

    def test_empty_database(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            find_nearest([], [0.0, 1.0])

    def test_zero_dimension(self):
        with self.assertRaisesRegex(ValueError, "at least one dimension"):
            find_nearest([[]], [])

    def test_flat_and_nested_representations_agree(self):
        vectors = [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]]
        flat_vectors = [value for vector in vectors for value in vector]
        expected = find_nearest(vectors, [1.0, 2.0])
        self.assertEqual(find_nearest_flat(flat_vectors, [1.0, 2.0], 2), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
