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
`build/memory_example` and `build/memory_views` for Activity 10 without running
either memory program. Work in your personal activity copy as directed on the
activity page. For each program, follow its labeled source-reading steps,
answer the guided which-object-changes questions, and sketch the relationships
before running that program. Full terminal-output predictions are not required:

```bash
./build/memory_example
# Answer the B2 questions and sketch memory_views.cpp before this next command.
./build/memory_views
```

`memory_example.cpp` introduces an integer copy, a reference, a pointer, and a
borrowed vector reference. `memory_views.cpp` compares a vector copy with a
writable view of part of the original vector and a read-only view of all its
elements. Follow A1–A4 in `memory_example.cpp` and B1–B3 in `memory_views.cpp`.
The `TODO(student)` comments at A2/B2 mark prediction questions; A4/B3 mark
diagram checkpoints immediately before the first output statement. Answer in
the activity submission, not by filling in missing code. After running, use
the printed rows and source assignments to check your answers and finish
the diagrams with final values. Neither program resizes a vector while
borrowing its elements.
Activity 10 also supplies address-printing statements to add to your personal
copy after the first prediction/run cycle.

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
