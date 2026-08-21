#include "search_kernel.hpp"

#include "distance.hpp"

#include <limits>
#include <stdexcept>

namespace ecpe170 {

SearchResult find_nearest(std::span<const double> flat_vectors,
                          std::size_t vector_count,
                          std::size_t dimension,
                          std::span<const double> query) {
    if (vector_count == 0) {
        throw std::invalid_argument("vectors must be non-empty");
    }
    if (dimension == 0) {
        throw std::invalid_argument("vectors must have at least one dimension");
    }
    if (query.size() != dimension) {
        throw std::invalid_argument("vector and query dimensions must match");
    }
    if (vector_count > std::numeric_limits<std::size_t>::max() / dimension ||
        flat_vectors.size() != vector_count * dimension) {
        throw std::invalid_argument("flat vector data does not match its shape");
    }

    SearchResult best{0, std::numeric_limits<double>::infinity()};
    for (std::size_t row = 0; row < vector_count; ++row) {
        const auto candidate = flat_vectors.subspan(row * dimension, dimension);
        const double distance = squared_distance(candidate, query);

        // TODO(student): Explain why strictly less-than preserves the Python
        // baseline's smallest-index tie rule while less-than-or-equal does not.
        if (distance < best.squared_distance) {
            best = {row, distance};
        }
    }
    return best;
}

}  // namespace ecpe170
