#include <cstddef>

double squared_distance(const double* left, const double* right, std::size_t dimension) {
    double total = 0.0;
    for (std::size_t i = 0; i < dimension; ++i) {
        const double difference = left[i] - right[i];
        total += difference * difference;
    }
    return total;
}

std::size_t count_below(const double* values, std::size_t count, double threshold) {
    std::size_t matches = 0;
    for (std::size_t i = 0; i < count; ++i) {
        if (values[i] < threshold) {
            ++matches;
        }
    }
    return matches;
}
