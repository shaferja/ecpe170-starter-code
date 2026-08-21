#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <omp.h>

namespace {

struct CompactCounter {
    volatile std::uint64_t value = 0;
};

struct alignas(64) SeparatedCounter {
    volatile std::uint64_t value = 0;
};

struct Options {
    std::uint64_t iterations = 5000000;
    int trials = 5;
    int threads = 4;
};

std::uint64_t parse_size(const char* text, std::string_view name) {
    const std::string value(text);
    std::size_t used = 0;
    const auto parsed = std::stoull(value, &used);
    if (used != value.size() || parsed == 0) {
        throw std::invalid_argument(std::string(name) + " must be a positive integer");
    }
    return parsed;
}

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg(argv[i]);
        if (arg == "--iterations" && i + 1 < argc) {
            options.iterations = parse_size(argv[++i], "--iterations");
        } else if (arg == "--trials" && i + 1 < argc) {
            options.trials = static_cast<int>(parse_size(argv[++i], "--trials"));
        } else if (arg == "--threads" && i + 1 < argc) {
            options.threads = static_cast<int>(parse_size(argv[++i], "--threads"));
        } else {
            throw std::invalid_argument(
                "usage: false_sharing [--iterations N] [--trials N] [--threads N]");
        }
    }
    return options;
}

template <typename Counter>
std::pair<double, std::uint64_t> run_once(std::uint64_t iterations, int threads) {
    std::vector<Counter> counters(static_cast<std::size_t>(threads));
    const auto start = std::chrono::steady_clock::now();
#pragma omp parallel num_threads(threads)
    {
        const int thread_id = omp_get_thread_num();
        Counter& counter = counters[static_cast<std::size_t>(thread_id)];
        for (std::uint64_t i = 0; i < iterations; ++i) {
            counter.value = counter.value + 1;
        }
    }
    const auto stop = std::chrono::steady_clock::now();
    std::uint64_t total = 0;
    for (const Counter& counter : counters) {
        total += counter.value;
    }
    const double elapsed =
        std::chrono::duration<double, std::milli>(stop - start).count();
    return {elapsed, total};
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        const std::uint64_t expected = options.iterations *
                                       static_cast<std::uint64_t>(options.threads);
        std::vector<double> compact_times;
        std::vector<double> separated_times;
        bool correct = true;
        for (int trial = 0; trial < options.trials; ++trial) {
            if (trial % 2 == 0) {
                const auto compact = run_once<CompactCounter>(options.iterations, options.threads);
                const auto separated = run_once<SeparatedCounter>(options.iterations, options.threads);
                compact_times.push_back(compact.first);
                separated_times.push_back(separated.first);
                correct = correct && compact.second == expected && separated.second == expected;
            } else {
                const auto separated = run_once<SeparatedCounter>(options.iterations, options.threads);
                const auto compact = run_once<CompactCounter>(options.iterations, options.threads);
                separated_times.push_back(separated.first);
                compact_times.push_back(compact.first);
                correct = correct && compact.second == expected && separated.second == expected;
            }
        }

        const double compact_ms = median(compact_times);
        const double separated_ms = median(separated_times);
        std::cout << "threads=" << options.threads << " iterations_per_thread="
                  << options.iterations << " trials=" << options.trials
                  << " expected_total=" << expected << '\n';
        std::cout << "layout,median_ms,total,correct\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "compact," << compact_ms << ',' << expected << ','
                  << (correct ? "PASS" : "FAIL") << '\n';
        std::cout << "separated_64B," << separated_ms << ',' << expected << ','
                  << (correct ? "PASS" : "FAIL") << '\n';
        std::cout << "compact_over_separated_ratio=" << compact_ms / separated_ms << '\n';
        return correct ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
