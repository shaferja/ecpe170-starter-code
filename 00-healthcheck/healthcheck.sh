#!/usr/bin/env bash

# ECPE 170 personal Linux VM readiness check.
# This script intentionally collects every blocking failure before exiting.

set -u

failures=0
tmp_dir=""

pass() {
    printf '[PASS] %s\n' "$1"
}

warn() {
    printf '[WARN] %s\n' "$1"
}

fail() {
    printf '[FAIL] %s\n' "$1"
    failures=$((failures + 1))
}

check_command() {
    local label="$1"
    local command_name="$2"
    local package_name="$3"

    if command -v "$command_name" >/dev/null 2>&1; then
        pass "$label: $(command -v "$command_name")"
    else
        fail "$label is missing (install package: $package_name)"
    fi
}

cleanup() {
    if [[ -n "$tmp_dir" && -d "$tmp_dir" ]]; then
        rm -rf "$tmp_dir"
    fi
}

trap cleanup EXIT

printf '%s\n' 'ECPE 170 personal Linux VM health check'
printf 'Run at: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'Kernel: %s\n' "$(uname -sr 2>/dev/null || printf 'unavailable')"
printf '\n%s\n' '== Platform =='

os_id=""
os_version=""
os_pretty="unknown operating system"
if [[ -r /etc/os-release ]]; then
    # Ubuntu's os-release file contains shell-safe assignments.
    # shellcheck disable=SC1091
    . /etc/os-release
    os_id="${ID:-}"
    os_version="${VERSION_ID:-}"
    os_pretty="${PRETTY_NAME:-${NAME:-unknown operating system}}"
fi

printf 'Operating system: %s\n' "$os_pretty"
if [[ "$os_id" == "ubuntu" && "$os_version" == "26.04" ]]; then
    pass "Ubuntu 26.04 course operating system"
else
    warn "$os_pretty detected; the official class VM is Ubuntu 26.04. Continuing with the remaining capability checks."
fi

architecture="$(uname -m 2>/dev/null || printf 'unknown')"
case "$architecture" in
    x86_64|amd64)
        architecture_label="AMD64 ($architecture)"
        pass "Supported native architecture: $architecture_label"
        ;;
    aarch64|arm64)
        architecture_label="ARM64 ($architecture)"
        pass "Supported native architecture: $architecture_label"
        ;;
    *)
        architecture_label="unsupported ($architecture)"
        fail "Unsupported architecture: $architecture; expected x86_64 (AMD64) or aarch64 (ARM64)"
        ;;
esac
printf 'Architecture: %s\n' "$architecture_label"

printf '\n%s\n' '== Required commands =='
check_command "GNU C compiler (build-essential)" gcc build-essential
check_command "GNU C++ compiler" g++ g++
check_command "Make" make make
check_command "CMake" cmake cmake
check_command "Git" git git
check_command "Python 3" python3 python3
check_command "GDB" gdb gdb
check_command "Valgrind" valgrind valgrind
check_command "Hyperfine" hyperfine hyperfine
check_command "curl" curl curl
check_command "wget" wget wget
check_command "unzip" unzip unzip
check_command "htop" htop htop
check_command "ifconfig (net-tools)" ifconfig net-tools
check_command "ip (iproute2)" ip iproute2
check_command "ping" ping iputils-ping
check_command "SSH client" ssh openssh-client
check_command "pkg-config" pkg-config pkg-config
check_command "Node.js" node nodejs
check_command "npm" npm npm

if command -v code >/dev/null 2>&1; then
    pass "Visual Studio Code: $(command -v code)"
else
    fail "Visual Studio Code is missing (follow the Microsoft APT-repository steps in the course setup guide, then install package: code)"
fi

printf '\n%s\n' '== Versions and Python capabilities =='
if command -v python3 >/dev/null 2>&1; then
    pass "$(python3 --version 2>&1)"

    if python3 -m pip --version >/dev/null 2>&1; then
        pass "pip: $(python3 -m pip --version 2>&1)"
    else
        fail "python3 -m pip failed (install package: python3-pip)"
    fi

    if python3 -c 'import numpy; print(numpy.__version__)' >/dev/null 2>&1; then
        numpy_version="$(python3 -c 'import numpy; print(numpy.__version__)' 2>/dev/null)"
        pass "NumPy import: version $numpy_version"
    else
        fail "NumPy import failed (install python3-numpy or install numpy in the active course virtual environment)"
    fi
else
    fail "Python capability checks could not run because python3 is missing"
fi

if command -v git >/dev/null 2>&1; then
    pass "$(git --version 2>&1)"
fi
if command -v g++ >/dev/null 2>&1; then
    pass "$(g++ --version 2>&1 | head -n 1)"
fi
if command -v cmake >/dev/null 2>&1; then
    pass "$(cmake --version 2>&1 | head -n 1)"
fi
if command -v make >/dev/null 2>&1; then
    pass "$(make --version 2>&1 | head -n 1)"
fi
if command -v code >/dev/null 2>&1; then
    pass "Visual Studio Code version: $(code --version 2>&1 | head -n 1)"

    printf '\n%s\n' '== Required VS Code extensions =='
    if vscode_extensions="$(code --list-extensions 2>/dev/null)"; then
        if printf '%s\n' "$vscode_extensions" | grep -Fqx 'ms-python.python'; then
            pass "VS Code Python extension: ms-python.python"
        else
            fail "VS Code Python extension is missing (install with: code --install-extension ms-python.python)"
        fi

        if printf '%s\n' "$vscode_extensions" | grep -Fqx 'ms-vscode.cpptools'; then
            pass "VS Code C/C++ extension: ms-vscode.cpptools"
        else
            fail "VS Code C/C++ extension is missing (install with: code --install-extension ms-vscode.cpptools)"
        fi
    else
        fail "Could not list VS Code extensions (run: code --list-extensions)"
    fi
fi

tmp_dir="$(mktemp -d 2>/dev/null || true)"
if [[ -z "$tmp_dir" || ! -d "$tmp_dir" ]]; then
    fail "Could not create a temporary directory for capability checks"
else
    printf '\n%s\n' '== Build capabilities =='

    if command -v python3 >/dev/null 2>&1; then
        if python3 -m venv "$tmp_dir/venv" >/dev/null 2>&1; then
            pass "Python virtual environments (python3-venv)"
        else
            fail "Python virtual-environment creation failed (install package: python3-venv)"
        fi
    fi

    if command -v python3-config >/dev/null 2>&1 && command -v g++ >/dev/null 2>&1; then
        cat > "$tmp_dir/python_headers.cpp" <<'CPP'
#include <Python.h>
int main() { return PY_MAJOR_VERSION < 3; }
CPP
        # Intentional word splitting expands the include flags from python3-config.
        # shellcheck disable=SC2046
        if g++ -std=c++20 $(python3-config --includes) -c "$tmp_dir/python_headers.cpp" -o "$tmp_dir/python_headers.o" >/dev/null 2>&1; then
            pass "Python development headers (python3-dev)"
        else
            fail "Python development-header compile failed (install package: python3-dev)"
        fi
    else
        fail "python3-config or g++ is missing, so Python development headers could not be checked (install python3-dev and g++)"
    fi

    if command -v python3 >/dev/null 2>&1 && python3 -c 'import pybind11' >/dev/null 2>&1; then
        pybind_version="$(python3 -c 'import pybind11; print(pybind11.__version__)' 2>/dev/null)"
        pass "pybind11 Python module: version $pybind_version"
    elif command -v python3-config >/dev/null 2>&1 && command -v g++ >/dev/null 2>&1; then
        cat > "$tmp_dir/pybind_headers.cpp" <<'CPP'
#include <pybind11/pybind11.h>
int main() { return 0; }
CPP
        # shellcheck disable=SC2046
        if g++ -std=c++20 $(python3-config --includes) -c "$tmp_dir/pybind_headers.cpp" -o "$tmp_dir/pybind_headers.o" >/dev/null 2>&1; then
            pass "pybind11 C++ headers (pybind11-dev)"
        else
            fail "pybind11 is unavailable to Python and its C++ headers did not compile (install pybind11-dev or pybind11 in the active course virtual environment)"
        fi
    else
        fail "pybind11 could not be checked because Python development tools or g++ are missing"
    fi

    if command -v g++ >/dev/null 2>&1; then
        cat > "$tmp_dir/openmp_check.cpp" <<'CPP'
#include <omp.h>
int main() {
    int count = 0;
    #pragma omp parallel reduction(+:count)
    count += 1;
    return count < 1;
}
CPP
        if g++ -std=c++20 -fopenmp "$tmp_dir/openmp_check.cpp" -o "$tmp_dir/openmp_check" >/dev/null 2>&1 && "$tmp_dir/openmp_check" >/dev/null 2>&1; then
            pass "OpenMP compile and run with g++ -fopenmp"
        else
            fail "OpenMP compile/run failed (repair the native g++/build-essential toolchain)"
        fi
    else
        fail "OpenMP could not be checked because g++ is missing"
    fi
fi

printf '\n%s\n' '== Setup receipt summary =='
printf 'Operating system: %s\n' "$os_pretty"
printf 'Architecture: %s\n' "$architecture_label"
printf 'Blocking failures: %d\n' "$failures"

if (( failures == 0 )); then
    printf '%s\n' 'RESULT: READY for ECPE 170'
    exit 0
fi

printf '%s\n' 'RESULT: NOT READY -- repair every [FAIL] item and rerun the complete check'
exit 1
