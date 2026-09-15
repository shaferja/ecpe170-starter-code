"""Checks for CSV validation and faithful plotting of benchmark measurements."""

import csv
from pathlib import Path
import tempfile
import unittest

try:
    import matplotlib
except ImportError as error:
    raise unittest.SkipTest("Plot tests require the Activity 08 matplotlib dependency") from error
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_numpy_results import VERSIONS, make_figure, read_results


class PlotResultsTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "results.csv"
        self.rows = [
            [name, "search only" if i != 1 else "conversion plus search", median, median / 2, median * 2]
            for i, (name, median) in enumerate(zip(VERSIONS, [0.1, 0.2, 0.025]))
        ]

    def write_rows(self, rows):
        with self.path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["version", "timed_scope", "median_s", "min_s", "max_s"])
            writer.writerows(rows)

    def test_reordered_csv_still_uses_python_as_reference(self):
        self.write_rows(list(reversed(self.rows)))
        rows = read_results(self.path)
        fig = make_figure(rows, "example.csv")
        self.addCleanup(plt.close, fig)
        self.assertEqual([bar.get_height() for bar in fig.axes[0].patches], [100, 200, 25])
        # A slower conversion path must appear below 1x, rather than as a speedup.
        self.assertEqual([bar.get_height() for bar in fig.axes[1].patches], [1, .5, 4])
        self.assertTrue(all(ax.get_ylim()[0] == 0 for ax in fig.axes))

    def test_missing_or_duplicate_versions_are_rejected(self):
        for rows in [self.rows[:-1], self.rows + [self.rows[0]]]:
            with self.subTest(rows=rows):
                self.write_rows(rows)
                with self.assertRaises(ValueError):
                    read_results(self.path)

    def test_nonfinite_negative_zero_or_unordered_times_are_rejected(self):
        for median in ["nan", "inf", -1, 0, 99]:
            with self.subTest(median=median):
                rows = [row[:] for row in self.rows]
                rows[0][2] = median
                self.write_rows(rows)
                with self.assertRaises(ValueError):
                    read_results(self.path)

    def test_missing_columns_are_rejected(self):
        self.path.write_text("version,median_s\npython_nested,0.1\n")
        with self.assertRaisesRegex(ValueError, "CSV must contain"):
            read_results(self.path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
