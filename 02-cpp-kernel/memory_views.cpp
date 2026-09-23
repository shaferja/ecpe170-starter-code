#include <iostream>
#include <span>
#include <vector>

int main() {
    std::vector<double> samples{2.0, 4.0, 6.0};
    std::vector<double> copied_samples = samples;
    std::span<double> tail = std::span<double>{samples}.subspan(1);
    std::span<const double> read_only{samples};

    tail[0] += 10.0;
    copied_samples[2] = 99.0;

    // TODO(student): Before running, predict both lines and draw the objects
    // at this checkpoint. Show separate copies, view ranges, write permissions,
    // and lifetimes. The vectors are not resized while these views exist.
    std::cout << read_only[0] << ' ' << read_only[1] << ' '
              << read_only[2] << '\n';
    std::cout << copied_samples[0] << ' ' << copied_samples[1] << ' '
              << copied_samples[2] << '\n';
}
