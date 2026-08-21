"""Profile only the vector-search workload, excluding input generation."""

from __future__ import annotations

import argparse
import cProfile
import io
import pstats
from pathlib import Path

from vector_search_benchmark import make_inputs, make_search, positive_int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors", type=positive_int, default=5_000)
    parser.add_argument("--dimension", "--dim", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=20)
    parser.add_argument("--repetitions", type=positive_int, default=3)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--representation", choices=("nested", "flat"),
                        default="nested")
    parser.add_argument("--sort", choices=("cumulative", "tottime", "calls"),
                        default="cumulative")
    parser.add_argument("--limit", type=positive_int, default=20)
    parser.add_argument("--output", type=Path,
                        help="write the readable profile to this text file")
    return parser.parse_args()


def run_workload(search, queries, repetitions: int) -> tuple[int, float]:
    index_checksum = 0
    distance_checksum = 0.0
    for _ in range(repetitions):
        for query in queries:
            index, distance = search(query)
            index_checksum += index
            distance_checksum += distance
    return index_checksum, distance_checksum


def main() -> None:
    args = parse_args()
    vectors, queries = make_inputs(
        args.vectors, args.dimension, args.queries, args.seed
    )
    search = make_search(vectors, args.dimension, args.representation)

    profiler = cProfile.Profile()
    profiler.enable()
    checksum = run_workload(search, queries, args.repetitions)
    profiler.disable()

    stream = io.StringIO()
    print(f"representation: {args.representation}", file=stream)
    print("profiled_scope: exact search only; setup/conversion excluded", file=stream)
    print(f"checksum: {checksum[0]}, {checksum[1]:.12f}", file=stream)
    print(file=stream)
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(
        args.sort
    ).print_stats(args.limit)
    report = stream.getvalue()

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote profile to {args.output}")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
