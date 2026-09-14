"""Correctness contract for the ECPE 170 Python vector-search baseline."""

import unittest

from vector_search_baseline import find_nearest, find_nearest_flat


class VectorSearchContractTests(unittest.TestCase):
    # A single candidate returns index 0 and its squared distance.
    def test_one_vector_input(self):
        # self.assertEqual(actual, expected) fails the test if the two values differ.
        self.assertEqual(find_nearest([[2.0, 3.0]], [5.0, 7.0]), (0, 25.0))

    # The closest of several candidates returns the expected index and squared distance.
    def test_known_nearest_vector(self):
        vectors = [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 2.0]), (2, 1.0))

    # An exact match returns the matching index and zero distance.
    def test_zero_distance(self):
        vectors = [[5.0, 5.0], [1.0, 2.0], [9.0, 9.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 2.0]), (1, 0.0))

    # Equally close candidates return the smallest index.
    def test_tie_returns_smallest_index(self):
        vectors = [[0.0, 0.0], [2.0, 0.0]]
        self.assertEqual(find_nearest(vectors, [1.0, 0.0]), (0, 1.0))

    # A candidate with a different dimension from the query raises ValueError.
    def test_dimension_mismatch(self):
        # self.assertRaisesRegex(type, pattern) requires the block to raise that exception with a message matching the regex.
        with self.assertRaisesRegex(ValueError, "dimensions must match"):
            find_nearest([[0.0, 1.0], [2.0]], [0.0, 1.0])

    # An empty candidate list raises ValueError.
    def test_empty_database(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            find_nearest([], [0.0, 1.0])

    # Vectors with no coordinates raise ValueError.
    def test_zero_dimension(self):
        with self.assertRaisesRegex(ValueError, "at least one dimension"):
            find_nearest([[]], [])

    # Flat and nested storage return the same index and squared distance.
    def test_flat_and_nested_representations_agree(self):
        vectors = [[0.0, 0.0], [3.0, 4.0], [1.0, 1.0]]
        flat_vectors = [value for vector in vectors for value in vector]
        expected = find_nearest(vectors, [1.0, 2.0])
        self.assertEqual(find_nearest_flat(flat_vectors, [1.0, 2.0], 2), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
