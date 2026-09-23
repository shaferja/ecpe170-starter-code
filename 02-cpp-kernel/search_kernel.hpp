#pragma once

#include <cstddef>
#include <span>

namespace ecpe170 {

// A search returns two related values. This struct groups them into one result:
// the selected vector's position and its squared distance from the query.
struct SearchResult {
    std::size_t index;         // Position of the selected vector (starting at 0).
    double squared_distance;  // Its squared distance from the query.
};

// This is a function declaration: it tells callers how to use find_nearest.
// The body is defined in search_kernel.cpp. The leading SearchResult is the
// return type: one object containing the two fields shown above. The four
// comma-separated parameters describe the database and the query to search for.
//
// Reading "std::span<const double> flat_vectors":
//   std::       selects a name from the C++ standard-library namespace.
//   span<...>  is a C++20 view of contiguous (adjacent-in-memory) elements.
//   const double means each element is a double that this view cannot modify.
//   flat_vectors is the parameter name: the database's coordinate sequence.
// Think of this span as a starting address plus an element count. It lets the
// function access existing coordinates without allocating or copying them.
// The query parameter has the same span type, but views just the query vector.
//
// The database stores each vector's coordinates consecutively in one flat
// sequence. For example, three vectors with two coordinates each occupy six
// consecutive elements. A span knows the total element count, but not how
// those elements are grouped into vectors. The next two parameters supply
// that shape: vector_count is the number of vectors, and dimension is the
// number of coordinates per vector. Their type, std::size_t, is the standard
// unsigned integer type used for sizes and indices.
//
// A span is non-owning: the caller must keep the underlying storage valid
// throughout the call. Passing a span by value copies only the small view,
// not the coordinates. This function reads through the views and does not
// keep them after returning. See distance.hpp for more about span syntax
// and how a view differs from a reference parameter.
//
// When reading the implementation, .size() gives a span's element count,
// [i] accesses one element, and .subspan(...) creates a view of part of the
// same storage. The programmer must use valid indices and ranges; C++20
// does not guarantee bounds checks for these operations.
//
// Contract: vector_count and dimension must be positive, query must contain
// exactly dimension elements, and flat_vectors must contain exactly
// vector_count * dimension elements (with that product representable in
// std::size_t). Invalid inputs cause std::invalid_argument. The smallest index
// wins a distance tie, matching the course Python baseline.
SearchResult find_nearest(std::span<const double> flat_vectors,
                          std::size_t vector_count,
                          std::size_t dimension,
                          std::span<const double> query);

}  // namespace ecpe170
