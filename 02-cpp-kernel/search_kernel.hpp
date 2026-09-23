#pragma once

#include <cstddef>
#include <span>

namespace ecpe170 {

// A struct groups the two values returned by find_nearest. The function returns
// this small result by value; it does not return a vector or a view of one.
struct SearchResult {
    std::size_t index;         // Position of the selected vector (starting at 0).
    double squared_distance;  // Its squared distance from the query.
};

// This declaration describes how to call find_nearest; search_kernel.cpp
// contains the function body. SearchResult before the name is the return type.
// Each comma-separated parameter below consists of a type followed by a name.
//
// std::span<const double> means a non-owning view of contiguous double elements:
//   std:: identifies a standard-library type; <...> specifies its element type.
//   span describes existing storage using a starting address and element count.
//   const double allows reading, but not changing, elements through this view.
// A span does not allocate, copy, or free the numeric data. Its .size() reports
// the number of elements; [i] accesses an element; .subspan(...) views a portion
// of the same storage without copying that portion. Indices and subspan ranges
// must be valid; C++20 does not guarantee bounds checks for these operations.
//
// The span objects are passed by value, so only the small views are copied.
// "Borrows" means the caller must keep the underlying storage valid during the
// call. It is an ownership/lifetime description, not pass-by-reference syntax:
// a C++ reference parameter has & in its type, and these parameters do not.
// This function does not retain the views after returning. See distance.hpp
// for a comparison with a const std::vector<double>& reference parameter.
//
// Parameters:
//   flat_vectors: one view containing all database coordinates, with each
//                 vector's coordinates stored consecutively (row by row).
//   vector_count: how many vectors those coordinates represent.
//   dimension:    how many coordinates each vector contains.
//   query:        a view of the query vector's coordinates.
// std::size_t is the standard unsigned integer type used for sizes and indices.
// vector_count and dimension are ordinary integer values passed by value.
// A span knows its element count, but not a table's row/column shape, so the
// function also needs vector_count and dimension to interpret flat_vectors.
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
