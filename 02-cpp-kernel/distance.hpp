#pragma once

#include <span>

namespace ecpe170 {

// This is a function declaration: it tells callers the function's name,
// return type, and parameter types. The body is defined in distance.cpp.
// The leading double is the return type: one squared distance. The two
// comma-separated parameters name the coordinate sequences to compare.
//
// Reading "std::span<const double> left":
//   std::       selects a name from the C++ standard-library namespace.
//   span<...>  is a C++20 view of contiguous (adjacent-in-memory) elements.
//   const double means each element is a double that this view cannot modify.
//   left       is the parameter name; right has the same type and meaning.
// Think of this span as a starting address plus an element count. It provides
// left.size() and left[i], without allocating or copying the coordinate data.
// A std::vector<double> can supply such a view when this function is called.
//
// A span is non-owning: the caller must ensure the underlying storage stays
// valid throughout the call. "Borrows" describes that lifetime relationship;
// it is not a special C++ parameter-passing mode. These span objects are passed
// BY VALUE (there is no & in their parameter types). Copying a span copies the
// small view, not its elements. A reference parameter would instead use &,
// as in "const std::vector<double>& values". Both approaches can avoid copying
// the data, but a span can view different contiguous containers or part of one.
// This function neither stores the spans for later use nor owns their memory.
//
// Contract: left and right must be nonempty and have equal lengths. Otherwise,
// the implementation throws std::invalid_argument. const prevents modification
// through these views; it does not make the caller's original container const.
// In C++20, span's operator[] does not guarantee bounds checking: callers of
// that operator must still use a valid index.
double squared_distance(std::span<const double> left,
                        std::span<const double> right);

}  // namespace ecpe170
