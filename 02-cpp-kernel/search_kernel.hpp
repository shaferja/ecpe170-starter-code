#pragma once

#include <cstddef>
#include <span>

namespace ecpe170 {

struct SearchResult {
    std::size_t index;
    double squared_distance;
};

// flat_vectors contains vector_count consecutive rows, each with dimension
// float64 values. query contains exactly dimension values. The smallest index
// wins a distance tie, matching the course Python baseline.
SearchResult find_nearest(std::span<const double> flat_vectors,
                          std::size_t vector_count,
                          std::size_t dimension,
                          std::span<const double> query);

}  // namespace ecpe170
