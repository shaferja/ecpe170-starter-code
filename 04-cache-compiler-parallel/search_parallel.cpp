#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <omp.h>

namespace {

struct Result {
    std::size_t index = 0;
    double distance = std::numeric_limits<double>::infinity();
};

struct Options {
    std::size_t vectors = 200000;
    std::size_t dimension = 64;
    int trials = 5;
    std::vector<int> thread_counts{1, 2, 4};
};

bool better(const Result& candidate, const Result& current) {
    return candidate.distance < current.distance ||
           (candidate.distance == current.distance && candidate.index < current.index);
}

double distance_at(
    const std::vector<double>& database,
    const std::vector<double>& query,
    std::size_t vector_index,
    std::size_t dimension) {
    const std::size_t start = vector_index * dimension;
    double total = 0.0;
    for (std::size_t i = 0; i < dimension; ++i) {
        const double difference = database[start + i] - query[i];
        total += difference * difference;
    }
    return total;
}

Result serial_search(
    const std::vector<double>& database,
    const std::vector<double>& query,
    std::size_t vector_count,
    std::size_t dimension) {
    Result best;
    for (std::size_t index = 0; index < vector_count; ++index) {
        const Result candidate{index, distance_at(database, query, index, dimension)};
        if (better(candidate, best)) {
            best = candidate;
        }
    }
    return best;
}

Result parallel_search(
    const std::vector<double>& database,
    const std::vector<double>& query,
    std::size_t vector_count,
    std::size_t dimension,
    int thread_count) {
    std::vector<Result> local_results(static_cast<std::size_t>(thread_count));

#pragma omp parallel num_threads(thread_count)
    {
        const int thread_id = omp_get_thread_num();
        Result local_best;
#pragma omp for schedule(static)
        for (std::size_t index = 0; index < vector_count; ++index) {
            const Result candidate{index, distance_at(database, query, index, dimension)};
            if (better(candidate, local_best)) {
                local_best = candidate;
            }
        }
        local_results[static_cast<std::size_t>(thread_id)] = local_best;
    }

    Result best;
    for (const Result& candidate : local_results) {
        if (better(candidate, best)) {
            best = candidate;
        }
    }
    return best;
}

std::size_t parse_size(const char* text, std::string_view name) {
    const std::string value(text);
    std::size_t used = 0;
    const auto parsed = std::stoull(value, &used);
    if (used != value.size() || parsed == 0) {
        throw std::invalid_argument(std::string(name) + " must be a positive integer");
    }
    return static_cast<std::size_t>(parsed);
}

std::vector<int> parse_threads(const std::string& text) {
    std::vector<int> counts;
    std::size_t start = 0;
    while (start < text.size()) {
        const std::size_t comma = text.find(',', start);
        const std::string part = text.substr(start, comma - start);
        const std::size_t count = parse_size(part.c_str(), "--threads");
        counts.push_back(static_cast<int>(count));
        if (comma == std::string::npos) {
            break;
        }
        start = comma + 1;
    }
    if (counts.empty()) {
        throw std::invalid_argument("--threads requires comma-separated counts");
    }
    return counts;
}

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg(argv[i]);
        if (arg == "--vectors" && i + 1 < argc) {
            options.vectors = parse_size(argv[++i], "--vectors");
        } else if (arg == "--dim" && i + 1 < argc) {
            options.dimension = parse_size(argv[++i], "--dim");
        } else if (arg == "--trials" && i + 1 < argc) {
            options.trials = static_cast<int>(parse_size(argv[++i], "--trials"));
        } else if (arg == "--threads" && i + 1 < argc) {
            options.thread_counts = parse_threads(argv[++i]);
        } else {
            throw std::invalid_argument(
                "usage: search_parallel [--vectors N] [--dim N] [--trials N] [--threads 1,2,4]");
        }
    }
    if (options.vectors > static_cast<std::size_t>(-1) / options.dimension) {
        throw std::invalid_argument("vectors * dimension is too large");
    }
    return options;
}

template <typename Function>
std::pair<double, Result> benchmark(int trials, Function&& function) {
    std::vector<double> times;
    Result result;
    result = function();
    for (int trial = 0; trial < trials; ++trial) {
        const auto start = std::chrono::steady_clock::now();
        result = function();
        const auto stop = std::chrono::steady_clock::now();
        times.push_back(std::chrono::duration<double, std::milli>(stop - start).count());
    }
    std::sort(times.begin(), times.end());
    return {times[times.size() / 2], result};
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        std::vector<double> database(options.vectors * options.dimension);
        std::vector<double> query(options.dimension);
        for (std::size_t i = 0; i < database.size(); ++i) {
            database[i] = static_cast<double>((i * 17 + 3) % 101) / 10.0;
        }
        for (std::size_t i = 0; i < query.size(); ++i) {
            query[i] = static_cast<double>((i * 13 + 7) % 97) / 10.0;
        }

        const auto [serial_ms, serial_result] = benchmark(options.trials, [&] {
            return serial_search(database, query, options.vectors, options.dimension);
        });

        std::cout << "vectors=" << options.vectors << " dim=" << options.dimension
                  << " trials=" << options.trials
                  << " openmp_max_threads=" << omp_get_max_threads() << '\n';
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "mode,threads,median_ms,speedup,best_index,best_distance,correct\n";
        std::cout << "serial,1," << serial_ms << ",1.000," << serial_result.index << ','
                  << serial_result.distance << ",PASS\n";

        bool all_correct = true;
        for (const int threads : options.thread_counts) {
            const auto [parallel_ms, result] = benchmark(options.trials, [&] {
                return parallel_search(
                    database, query, options.vectors, options.dimension, threads);
            });
            const bool correct = result.index == serial_result.index &&
                                 std::abs(result.distance - serial_result.distance) < 1e-9;
            all_correct = all_correct && correct;
            std::cout << "parallel," << threads << ',' << parallel_ms << ','
                      << serial_ms / parallel_ms << ',' << result.index << ','
                      << result.distance << ',' << (correct ? "PASS" : "FAIL") << '\n';
        }
        return all_correct ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
