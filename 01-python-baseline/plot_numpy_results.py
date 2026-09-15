"""Plot the three timing rows emitted by numpy_vector_search.py."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

VERSIONS = (
    "python_nested", "numpy_conversion_included", "numpy_preconverted"
)
LABELS = ("Python lists", "NumPy\nconversion included", "NumPy\nalready converted")


def read_results(path: Path) -> list[dict]:
    """Require one complete benchmark, with finite, ordered timing summaries."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"version", "timed_scope", "median_s", "min_s", "max_s"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must contain version,timed_scope,median_s,min_s,max_s")
        rows = {}
        for row in reader:
            name = row["version"]
            if name not in VERSIONS or name in rows:
                raise ValueError(f"Unexpected or repeated version: {name!r}; use one benchmark CSV")
            try:
                times = {key: float(row[key]) for key in ("min_s", "median_s", "max_s")}
            except (ValueError, TypeError) as error:
                raise ValueError(f"{name}: timings must be numbers") from error
            if not all(math.isfinite(t) and t >= 0 for t in times.values()):
                raise ValueError(f"{name}: timings must be finite and nonnegative")
            if not 0 <= times["min_s"] <= times["median_s"] <= times["max_s"] or times["median_s"] == 0:
                raise ValueError(f"{name}: require 0 <= min <= median <= max and median > 0; rerun with more work")
            if not row["timed_scope"] or not row["timed_scope"].strip():
                raise ValueError(f"{name}: missing timed_scope")
            rows[name] = {**times, "timed_scope": row["timed_scope"].strip()}
    if set(rows) != set(VERSIONS):
        raise ValueError("CSV must include all three Python/NumPy versions")
    return [rows[name] for name in VERSIONS]


def make_figure(rows, source_name):
    """Show elapsed time and the Python/variant ratio without hiding timer scopes."""
    import matplotlib.pyplot as plt

    medians = [row["median_s"] * 1000 for row in rows]
    errors = [[(row["median_s"] - row["min_s"]) * 1000 for row in rows],
              [(row["max_s"] - row["median_s"]) * 1000 for row in rows]]
    ratios = [medians[0] / value for value in medians]
    colors = ["#475569", "#dc8a24", "#15847b"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.6))
    fig.subplots_adjust(left=.08, right=.97, top=.82, bottom=.35, wspace=.3)
    fig.suptitle("Python vs NumPy: measured search performance", fontsize=17, fontweight="bold", y=.96)
    fig.text(.5, .89, source_name, ha="center", fontsize=10, color="#475569")
    axes[0].bar(range(3), medians, color=colors, yerr=errors, capsize=5)
    axes[0].set_title("Elapsed time — lower is better", fontsize=12)
    axes[0].set_ylabel("Milliseconds for all queries")
    axes[0].set_ylim(0, max(row["max_s"] * 1000 for row in rows) * 1.25)
    for i, value in enumerate(medians):
        axes[0].annotate(f"{value:.3g} ms", (i, rows[i]["max_s"] * 1000),
                         xytext=(0, 8), textcoords="offset points", ha="center")
    axes[1].bar(range(3), ratios, color=colors)
    axes[1].axhline(1, color="#475569", linestyle="--", linewidth=1)
    axes[1].set_title("Relative speed — higher is better", fontsize=12)
    axes[1].set_ylabel("Python median / variant median")
    axes[1].set_ylim(0, max(ratios) * 1.25)
    for i, value in enumerate(ratios):
        axes[1].annotate(f"{value:.2f}×", (i, value), xytext=(0, 8),
                         textcoords="offset points", ha="center")
    for ax in axes:
        ax.set_xticks(range(3), LABELS)
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
    fig.text(.08, .21, "Bars: medians. Whiskers: observed minimum–maximum, not confidence intervals.", fontsize=10)
    for i, (name, row) in enumerate(zip(VERSIONS, rows)):
        fig.text(.08, .165 - i * .035, f"{name}: {row['timed_scope']}", fontsize=9)
    fig.text(.08, .025, "Ratios compare the labeled scopes; preconverted search excludes conversion. Results may show a slowdown.", fontsize=9)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="CSV saved from one numpy_vector_search.py run")
    parser.add_argument("--save", type=Path, help="also save a PNG (for example results/activity08-numpy.png)")
    parser.add_argument("--no-show", action="store_true", help="save without opening a window (requires --save)")
    args = parser.parse_args()
    if args.no_show and args.save is None:
        parser.error("--no-show requires --save")
    if args.save and args.save.suffix.lower() != ".png":
        parser.error("--save must name a .png file")
    try:
        rows = read_results(args.csv)
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))
    try:
        import matplotlib
        if args.no_show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        parser.error("Install Matplotlib in your activity environment: python3 -m pip install matplotlib")
    fig = make_figure(rows, args.csv.name)
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.save, dpi=160)
        print(f"Saved graph: {args.save}")
    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
