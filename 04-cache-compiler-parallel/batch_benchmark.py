#!/usr/bin/env python3
"""Compare compute-only vector-search batching and blocking choices."""

from __future__ import annotations

import argparse
import platform
import random
import statistics
import time


def positive_int(text: str) -> int:
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return value


def batch_sizes(text: str) -> list[int]:
    try:
        values = [positive_int(item.strip()) for item in text.split(",")]
    except (ValueError, argparse.ArgumentTypeError) as error:
        raise argparse.ArgumentTypeError("use comma-separated positive integers") from error
    if not values:
        raise argparse.ArgumentTypeError("at least one batch size is required")
    return values


def make_inputs(vectors: int, dimension: int, queries: int, seed: int) -> tuple[list[list[float]], list[list[float]]]:
    rng = random.Random(seed)
    database = [
        [float(rng.randrange(-8, 9)) for _ in range(dimension)]
        for _ in range(vectors)
    ]
    query_data = [
        [float(rng.randrange(-8, 9)) for _ in range(dimension)]
        for _ in range(queries)
    ]
    return database, query_data


def search_batched(
    database: list[list[float]],
    queries: list[list[float]],
    batch_size: int,
    block_size: int,
) -> tuple[int, ...]:
    answers: list[int] = []
    for batch_start in range(0, len(queries), batch_size):
        batch = queries[batch_start : batch_start + batch_size]
        best_indices = [-1] * len(batch)
        best_distances = [float("inf")] * len(batch)

        for block_start in range(0, len(database), block_size):
            block = database[block_start : block_start + block_size]
            for offset, vector in enumerate(block):
                vector_index = block_start + offset
                for query_index, query in enumerate(batch):
                    distance = 0.0
                    for left, right in zip(vector, query):
                        difference = left - right
                        distance += difference * difference
                    if distance < best_distances[query_index]:
                        best_distances[query_index] = distance
                        best_indices[query_index] = vector_index

        answers.extend(best_indices)
    return tuple(answers)


def time_configuration(
    database: list[list[float]],
    queries: list[list[float]],
    batch_size: int,
    block_size: int,
    warmups: int,
    trials: int,
) -> tuple[float, tuple[int, ...]]:
    answer: tuple[int, ...] = ()
    for _ in range(warmups):
        answer = search_batched(database, queries, batch_size, block_size)

    elapsed_ms: list[float] = []
    for _ in range(trials):
        start = time.perf_counter()
        answer = search_batched(database, queries, batch_size, block_size)
        elapsed_ms.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(elapsed_ms), answer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", type=positive_int, default=512)
    parser.add_argument("--dim", type=positive_int, default=32)
    parser.add_argument("--queries", type=positive_int, default=64)
    parser.add_argument("--batch-sizes", type=batch_sizes, default=[1, 4, 16])
    parser.add_argument("--block-size", type=positive_int, default=64)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--trials", type=positive_int, default=5)
    parser.add_argument("--seed", type=int, default=170)
    args = parser.parse_args()
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")

    database, queries = make_inputs(args.vectors, args.dim, args.queries, args.seed)
    print(
        f"architecture={platform.machine()} vectors={args.vectors} dim={args.dim} "
        f"queries={args.queries} block_size={args.block_size} seed={args.seed}"
    )
    print("timed_scope=compute only; excludes input generation, queue wait, and networking")
    print("batch_size,median_compute_ms,latency_per_query_ms,throughput_qps,checksum,correct")

    reference: tuple[int, ...] | None = None
    all_correct = True
    for size in args.batch_sizes:
        elapsed_ms, answer = time_configuration(
            database, queries, size, args.block_size, args.warmups, args.trials
        )
        if reference is None:
            reference = answer
        correct = answer == reference
        all_correct = all_correct and correct
        latency = elapsed_ms / args.queries
        throughput = args.queries / (elapsed_ms / 1000.0)
        checksum = sum((index + 1) * value for index, value in enumerate(answer))
        print(
            f"{size},{elapsed_ms:.3f},{latency:.6f},{throughput:.3f},"
            f"{checksum},{'PASS' if correct else 'FAIL'}"
        )
    return 0 if all_correct else 1


if __name__ == "__main__":
    raise SystemExit(main())
