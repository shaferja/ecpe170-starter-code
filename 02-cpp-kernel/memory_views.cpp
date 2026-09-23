#include <iostream>
#include <span>
#include <vector>

int main() {
    // B1: Read these declarations and sketch the vectors and view ranges.
    std::vector<double> samples{2.0, 4.0, 6.0};
    std::vector<double> copied_samples = samples;
    std::span<double> tail = std::span<double>{samples}.subspan(1);
    std::span<const double> read_only{samples};

    // TODO(student): B2 - Before running, answer Activity 10 Response 4.
    // Which element changes, and which names can see each change below?
    // Explain your choices; complete terminal-output predictions are not required.
    tail[0] += 10.0;
    copied_samples[2] = 99.0;

    // TODO(student): B3 - Diagram B checkpoint (Activity 10 Response 5).
    // Sketch relationships before running; use output to finish values afterward.
    // Each statement below spans two source lines but prints one terminal row.
    // Compare these rows with your B2 reasoning in Response 4.
    // The vectors are not resized while these views exist.
    std::cout << read_only[0] << ' ' << read_only[1] << ' '
              << read_only[2] << '\n';
    std::cout << copied_samples[0] << ' ' << copied_samples[1] << ' '
              << copied_samples[2] << '\n';
}
