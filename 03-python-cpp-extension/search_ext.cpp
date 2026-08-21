#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "search_kernel.hpp"

#include <cstddef>
#include <span>
#include <string>

namespace py = pybind11;

namespace {

void require_float64_c_array(const py::array& array, const char* name) {
    if (!array.dtype().is(py::dtype::of<double>())) {
        throw py::value_error(std::string(name) + " must have dtype float64");
    }
    if ((array.flags() & py::array::c_style) == 0) {
        throw py::value_error(std::string(name) +
                              " must be C-contiguous (row-major)");
    }
}

py::tuple find_nearest(const py::array& vectors, const py::array& query) {
    // The wrapper rejects implicit dtype/layout conversion so boundary costs are
    // visible to the Python caller rather than hidden inside this function.
    require_float64_c_array(vectors, "vectors");
    require_float64_c_array(query, "query");

    if (vectors.ndim() != 2) {
        throw py::value_error("vectors must be a 2-D array");
    }
    if (query.ndim() != 1) {
        throw py::value_error("query must be a 1-D array");
    }
    if (vectors.shape(0) == 0) {
        throw py::value_error("vectors must be non-empty");
    }
    if (vectors.shape(1) == 0) {
        throw py::value_error("vectors must have at least one dimension");
    }
    if (vectors.shape(1) != query.shape(0)) {
        throw py::value_error("vector and query dimensions must match");
    }

    const py::buffer_info vector_info = vectors.request();
    const py::buffer_info query_info = query.request();
    const auto vector_count = static_cast<std::size_t>(vectors.shape(0));
    const auto dimension = static_cast<std::size_t>(vectors.shape(1));
    const auto flat_size = static_cast<std::size_t>(vector_info.size);
    const auto* vector_data = static_cast<const double*>(vector_info.ptr);
    const auto* query_data = static_cast<const double*>(query_info.ptr);

    ecpe170::SearchResult result{};
    {
        // The NumPy arrays remain alive for the whole call. The native kernel
        // borrows their buffers and never retains the pointers.
        py::gil_scoped_release release;
        result = ecpe170::find_nearest(
            std::span<const double>(vector_data, flat_size), vector_count,
            dimension, std::span<const double>(query_data, dimension));
    }

    return py::make_tuple(result.index, result.squared_distance);
}

}  // namespace

PYBIND11_MODULE(search_ext, module) {
    module.doc() = "ECPE 170 exact vector-search extension";
    module.def(
        "find_nearest", &find_nearest, py::arg("vectors"), py::arg("query"),
        R"doc(
Return (smallest best index, squared distance).

vectors must be a non-empty, 2-D, C-contiguous NumPy float64 array with shape
(vector_count, dimension). query must be a 1-D, C-contiguous NumPy float64 array
with shape (dimension,). Inputs are borrowed for this call and are not retained.
)doc");
    module.attr("boundary_contract") =
        "float64 C-contiguous vectors[n,d] + query[d] -> (index, squared_distance)";
}
