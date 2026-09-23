#include <iostream>
#include <vector>

int main() {
    // A1: Read these declarations and sketch the objects and arrows.
    int value = 5;
    int copied_value = value;
    int& reference = value;
    int* pointer = &value;

    // TODO(student): A2 - Before running, answer Activity 10 Response 2.
    // For each assignment below, predict which object changes and explain why.
    // You do not need to predict the complete terminal output.
    copied_value += 10;
    reference += 1;
    *pointer += 2;

    // A3: Add this vector and its borrowed reference to your sketch.
    const std::vector<double> query{1.0, 2.0};
    const std::vector<double>& borrowed_query = query;

    // TODO(student): A4 - Diagram A checkpoint (Activity 10 Response 3).
    // Sketch relationships before running; use output to finish values afterward.
    // These statements print two terminal rows: integers, then vector evidence.
    // Compare the output with your A2 reasoning in Response 2.
    // Add the activity's address-printing statements after these two statements.
    std::cout << value << ' ' << copied_value << '\n';
    std::cout << query.size() << ' ' << borrowed_query[0] << '\n';
}
