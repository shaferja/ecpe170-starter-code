#include "distance.hpp"
#include "search_kernel.hpp"

#include <cmath>
#include <exception>
#include <iostream>
#include <span>
#include <string_view>
#include <vector>

namespace {

int failures = 0;

void check(std::string_view name, bool condition) {
    std::cout << (condition ? "PASS " : "FAIL ") << name << '\n';
    if (!condition) {
        ++failures;
    }
}
bool close(double left, double right) {
    return std::abs(left - right) <= 1e-12;
}

}  // namespace

int main() {
    using ecpe170::find_nearest;

    const std::vector<double> one_vector{2.0, -1.0};
    const std::vector<double> one_query{2.0, 1.0};
    const auto one = find_nearest(one_vector, 1, 2, one_query);
    check("one_vector", one.index == 0 && close(one.squared_distance, 4.0));

    const std::vector<double> vectors{0.0, 0.0, 3.0, 4.0, 1.0, 1.0};
    const std::vector<double> query{1.0, 2.0};
    const auto known = find_nearest(vectors, 3, 2, query);
    check("known_nearest", known.index == 2 && close(known.squared_distance, 1.0));

    const std::vector<double> exact_query{3.0, 4.0};
    const auto exact = find_nearest(vectors, 3, 2, exact_query);
    check("zero_distance", exact.index == 1 && close(exact.squared_distance, 0.0));

    const std::vector<double> tied_vectors{0.0, 0.0, 2.0, 0.0};
    const std::vector<double> tied_query{1.0, 0.0};
    const auto tied = find_nearest(tied_vectors, 2, 2, tied_query);
    check("smallest_index_tie", tied.index == 0 && close(tied.squared_distance, 1.0));

    bool rejected_mismatch = false;
    try {
        const std::vector<double> short_query{1.0};
        static_cast<void>(find_nearest(vectors, 3, 2, short_query));
    } catch (const std::invalid_argument&) {
        rejected_mismatch = true;
    }
    check("dimension_mismatch", rejected_mismatch);

    std::cout << "summary: " << (5 - failures) << "/5 checks passed\n";
    return failures == 0 ? 0 : 1;
}
