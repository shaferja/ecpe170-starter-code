#include "distance.hpp"

#include <cstddef>
#include <stdexcept>

namespace ecpe170 {

double squared_distance(std::span<const double> left,
                        std::span<const double> right) {
    if (left.empty()) {
        throw std::invalid_argument("vectors must have at least one dimension");
    }
    if (left.size() != right.size()) {
        throw std::invalid_argument("vector and query dimensions must match");
    }

    double total = 0.0;
    for (std::size_t coordinate = 0; coordinate < left.size(); coordinate++) {
        const double difference = left[coordinate] - right[coordinate];
        total += difference * difference;
    }
    return total;
}

}  // namespace ecpe170
