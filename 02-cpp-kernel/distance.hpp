#pragma once

#include <span>

namespace ecpe170 {

// Both spans borrow read-only memory from their caller. This function neither
// owns nor retains that memory.
double squared_distance(std::span<const double> left,
                        std::span<const double> right);

}  // namespace ecpe170
