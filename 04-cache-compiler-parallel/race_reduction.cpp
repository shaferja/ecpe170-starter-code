#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <omp.h>

namespace {

struct Options {
    std::size_t items = 1000000;
    int repeats = 5;
    int threads = 4;
};

std::size_t parse_size(const char* text, std::string_view name) {
    const std::string value(text);
    std::size_t used = 0;
    const auto parsed = std::stoull(value, &used);
    if (used != value.size() || parsed == 0) {
        throw std::invalid_argument(std::string(name) + " must be a positive integer");
    }
    return static_cast<std::size_t>(parsed);
}

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg(argv[i]);
        if (arg == "--items" && i + 1 < argc) {
            options.items = parse_size(argv[++i], "--items");
        } else if (arg == "--repeats" && i + 1 < argc) {
            options.repeats = static_cast<int>(parse_size(argv[++i], "--repeats"));
        } else if (arg == "--threads" && i + 1 < argc) {
            options.threads = static_cast<int>(parse_size(argv[++i], "--threads"));
        } else {
            throw std::invalid_argument(
                "usage: race_reduction [--items N] [--repeats N] [--threads N]");
        }
    }
    return options;
}

long long unsafe_race_sum(const std::vector<int>& values, int threads) {
    long long total = 0;
#pragma omp parallel for num_threads(threads) schedule(static) shared(total)
    for (std::size_t i = 0; i < values.size(); ++i) {
        total += values[i];  // Intentionally unsafe shared read-modify-write.
    }
    return total;
}

long long reduction_sum(const std::vector<int>& values, int threads) {
    long long total = 0;
#pragma omp parallel for num_threads(threads) schedule(static) reduction(+ : total)
    for (std::size_t i = 0; i < values.size(); ++i) {
        total += values[i];
    }
    return total;
}

template <typename Function>
std::pair<long long, double> run_timed(Function&& function) {
    const auto start = std::chrono::steady_clock::now();
    const long long result = function();
    const auto stop = std::chrono::steady_clock::now();
    const double elapsed =
        std::chrono::duration<double, std::milli>(stop - start).count();
    return {result, elapsed};
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        const std::vector<int> values(options.items, 1);
        const long long expected = static_cast<long long>(options.items);

        std::cout << "items=" << options.items << " threads=" << options.threads
                  << " expected=" << expected << '\n';
        std::cout << "run,race_sum,race_status,reduction_sum,reduction_status,race_ms,reduction_ms\n";
        std::cout << std::fixed << std::setprecision(3);
        bool reductions_correct = true;
        for (int run = 1; run <= options.repeats; ++run) {
            const auto [race, race_ms] = run_timed(
                [&] { return unsafe_race_sum(values, options.threads); });
            const auto [reduction, reduction_ms] = run_timed(
                [&] { return reduction_sum(values, options.threads); });
            const bool reduction_correct = reduction == expected;
            reductions_correct = reductions_correct && reduction_correct;
            std::cout << run << ',' << race << ',' << (race == expected ? "LUCKY" : "WRONG")
                      << ',' << reduction << ',' << (reduction_correct ? "PASS" : "FAIL")
                      << ',' << race_ms << ',' << reduction_ms << '\n';
        }
        return reductions_correct ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
