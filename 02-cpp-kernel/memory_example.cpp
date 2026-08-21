#include <iostream>
#include <vector>

int main() {
    int value = 5;
    int copied_value = value;
    int& reference = value;
    int* pointer = &value;

    copied_value += 10;
    reference += 1;
    *pointer += 2;

    const std::vector<double> query{1.0, 2.0};
    const std::vector<double>& borrowed_query = query;

    // TODO(student): Predict both lines before running. In a memory diagram,
    // identify the owners, aliases, addresses, and lifetime of each object.
    std::cout << value << ' ' << copied_value << '\n';
    std::cout << query.size() << ' ' << borrowed_query[0] << '\n';
}
