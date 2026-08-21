#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

struct Options {
    std::size_t rows = 16384;
    std::size_t cols = 256;
    int trials = 7;
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
        if (arg == "--rows" && i + 1 < argc) {
            options.rows = parse_size(argv[++i], "--rows");
        } else if (arg == "--cols" && i + 1 < argc) {
            options.cols = parse_size(argv[++i], "--cols");
        } else if (arg == "--trials" && i + 1 < argc) {
            options.trials = static_cast<int>(parse_size(argv[++i], "--trials"));
        } else {
            throw std::invalid_argument("usage: cache_bench [--rows N] [--cols N] [--trials N]");
        }
    }
    if (options.rows > static_cast<std::size_t>(-1) / options.cols) {
        throw std::invalid_argument("rows * cols is too large");
    }
    return options;
}

double row_wise(const std::vector<double>& values, std::size_t rows, std::size_t cols) {
    double sum = 0.0;
    for (std::size_t row = 0; row < rows; ++row) {
        for (std::size_t col = 0; col < cols; ++col) {
            sum += values[row * cols + col];
        }
    }
    return sum;
}

double strided(const std::vector<double>& values, std::size_t rows, std::size_t cols) {
    double sum = 0.0;
    for (std::size_t col = 0; col < cols; ++col) {
        for (std::size_t row = 0; row < rows; ++row) {
            sum += values[row * cols + col];
        }
    }
    return sum;
}

template <typename Function>
double time_once(Function&& function, double& checksum) {
    const auto start = std::chrono::steady_clock::now();
    checksum = function();
    const auto stop = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::milli>(stop - start).count();
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    const std::size_t middle = values.size() / 2;
    if (values.size() % 2 == 1) {
        return values[middle];
    }
    return (values[middle - 1] + values[middle]) / 2.0;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        const std::size_t elements = options.rows * options.cols;
        std::vector<double> values(elements);
        for (std::size_t i = 0; i < elements; ++i) {
            values[i] = static_cast<double>((i % 13) + 1);
        }

        double warmup = row_wise(values, options.rows, options.cols);
        warmup += strided(values, options.rows, options.cols);
        if (warmup == 0.0) {
            return 2;
        }

        std::vector<double> row_times;
        std::vector<double> strided_times;
        double row_checksum = 0.0;
        double strided_checksum = 0.0;
        for (int trial = 0; trial < options.trials; ++trial) {
            if (trial % 2 == 0) {
                row_times.push_back(time_once(
                    [&] { return row_wise(values, options.rows, options.cols); }, row_checksum));
                strided_times.push_back(time_once(
                    [&] { return strided(values, options.rows, options.cols); }, strided_checksum));
            } else {
                strided_times.push_back(time_once(
                    [&] { return strided(values, options.rows, options.cols); }, strided_checksum));
                row_times.push_back(time_once(
                    [&] { return row_wise(values, options.rows, options.cols); }, row_checksum));
            }
        }

        const bool checksums_match = std::abs(row_checksum - strided_checksum) < 1e-9;
        std::cout << "rows=" << options.rows << " cols=" << options.cols
                  << " elements=" << elements << " trials=" << options.trials << '\n';
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "pattern,median_ms,checksum,correct\n";
        std::cout << "row-wise," << median(row_times) << ',' << row_checksum << ','
                  << (checksums_match ? "PASS" : "FAIL") << '\n';
        std::cout << "strided," << median(strided_times) << ',' << strided_checksum << ','
                  << (checksums_match ? "PASS" : "FAIL") << '\n';
        return checksums_match ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
