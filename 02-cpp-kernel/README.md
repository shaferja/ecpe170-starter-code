# C++ Vector-Search Kernel Starter Packet

These files provide a known-good native kernel for Activities 09-10. The same
kernel is wrapped by the pybind11 starter in `../03-python-cpp-extension/`.
Required work uses portable C++20 and runs natively on AMD64 (`x86_64`) and ARM64
(`aarch64`) Ubuntu; it contains no architecture-specific flags or intrinsics.

## Read the contract before the build command

`find_nearest` receives:

- one flat, row-major sequence containing `vector_count * dimension` `double`
  values;
- the vector count and dimension that describe that sequence; and
- one read-only query containing exactly `dimension` `double` values.

The function borrows its inputs for the duration of the call, retains no pointer,
and returns a value containing `(smallest best index, squared distance)`. It rejects
empty inputs and shape mismatches. A strict `<` comparison preserves the first
matching index on a tie, matching the Python reference contract.

Before compiling, locate each part of that contract in `search_kernel.hpp` and
`search_kernel.cpp`. Complete the `TODO(student)` explanation in your activity
submission; the starter remains runnable before you edit it.

## Build and run the checks

From this directory on your personal Linux VM:

```bash
chmod +x build_cpp.sh
./build_cpp.sh
```

The script uses `g++` by default. To select another C++20 compiler, set `CXX`, for
example `CXX=clang++ ./build_cpp.sh`. It creates the generated executable at
`build/kernel_driver`, runs five correctness checks, and also compiles
`build/memory_example` for Activity 10. Predict the memory example's output and
draw its ownership/aliasing diagram before running it:

```bash
./build/memory_example
```

You can also build manually:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  distance.cpp search_kernel.cpp kernel_driver.cpp \
  -o kernel_driver
./kernel_driver
```

Read the first compiler error first. Do not benchmark or wrap the kernel until all
checks pass. Exact paths and compiler versions can differ between machines; the
contract and check names should not.
