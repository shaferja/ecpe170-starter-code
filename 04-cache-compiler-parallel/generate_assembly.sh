#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

architecture="$(uname -m)"
case "$architecture" in
    x86_64|amd64)
        architecture_label="AMD64"
        ;;
    aarch64|arm64)
        architecture_label="ARM64"
        ;;
    *)
        architecture_label="unrecognized architecture"
        ;;
esac

syntax="native"
if [[ "${1:-}" == "--intel" ]]; then
    if [[ "$architecture" != "x86_64" && "$architecture" != "amd64" ]]; then
        echo "error: --intel is optional AMD64 enrichment and is not valid on $architecture" >&2
        exit 2
    fi
    syntax="intel"
elif [[ $# -ne 0 ]]; then
    echo "usage: ./generate_assembly.sh [--intel]" >&2
    exit 2
fi

cxx="${CXX:-g++}"
output_dir="assembly"
mkdir -p "$output_dir"

common_flags=(-std=c++20 -S -fverbose-asm)
suffix=""
if [[ "$syntax" == "intel" ]]; then
    common_flags+=(-masm=intel)
    suffix="_intel"
fi

"$cxx" "${common_flags[@]}" -O0 compiler_example.cpp \
    -o "$output_dir/compiler_example_O0${suffix}.s"
"$cxx" "${common_flags[@]}" -O3 compiler_example.cpp \
    -o "$output_dir/compiler_example_O3${suffix}.s"

echo "architecture=$architecture ($architecture_label)"
echo "compiler=$($cxx --version | head -n 1)"
echo "syntax=$syntax"
echo "generated=$output_dir/compiler_example_O0${suffix}.s"
echo "generated=$output_dir/compiler_example_O3${suffix}.s"
