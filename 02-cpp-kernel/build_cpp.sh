#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

CXX="${CXX:-g++}"
mkdir -p build

"$CXX" \
  -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  distance.cpp search_kernel.cpp kernel_driver.cpp \
  -o build/kernel_driver

"$CXX" \
  -std=c++20 -O0 -Wall -Wextra -Wpedantic \
  memory_example.cpp -o build/memory_example

echo "built: $(pwd)/build/kernel_driver"
./build/kernel_driver
echo "built: $(pwd)/build/memory_example"
