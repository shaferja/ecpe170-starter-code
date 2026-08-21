#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace {

std::pair<std::size_t, double> search(const double* database,
                                      std::size_t vector_count,
                                      std::size_t dimension,
                                      const double* query) {
    if (vector_count == 0 || dimension == 0) {
        throw std::invalid_argument("database must be non-empty");
    }
    std::size_t best_index = 0;
    double best_distance = std::numeric_limits<double>::infinity();
    for (std::size_t row = 0; row < vector_count; ++row) {
        double distance = 0.0;
        const double* vector = database + row * dimension;
        for (std::size_t column = 0; column < dimension; ++column) {
            const double difference = vector[column] - query[column];
            distance += difference * difference;
        }
        if (distance < best_distance) {
            best_index = row;
            best_distance = distance;
        }
    }
    return {best_index, best_distance};
}

std::pair<std::size_t, double> find_nearest_copy(const py::sequence& rows,
                                                  const py::sequence& query_values) {
    const std::size_t vector_count = py::len(rows);
    const std::size_t dimension = py::len(query_values);
    if (vector_count == 0 || dimension == 0) {
        throw py::value_error("database and query must be non-empty");
    }
    std::vector<double> database;
    database.reserve(vector_count * dimension);
    for (const py::handle row_handle : rows) {
        const py::sequence row = py::reinterpret_borrow<py::sequence>(row_handle);
        if (static_cast<std::size_t>(py::len(row)) != dimension) {
            throw py::value_error("database rows and query dimensions must match");
        }
        for (const py::handle value : row) {
            database.push_back(py::cast<double>(value));
        }
    }
    std::vector<double> query;
    query.reserve(dimension);
    for (const py::handle value : query_values) {
        query.push_back(py::cast<double>(value));
    }
    return search(database.data(), vector_count, dimension, query.data());
}

class NativeIndex {
  public:
    explicit NativeIndex(const py::array_t<double, py::array::c_style | py::array::forcecast>& input) {
        const py::buffer_info info = input.request();
        if (info.ndim != 2 || info.shape[0] <= 0 || info.shape[1] <= 0) {
            throw py::value_error("database must be a non-empty 2-D array");
        }
        vector_count_ = static_cast<std::size_t>(info.shape[0]);
        dimension_ = static_cast<std::size_t>(info.shape[1]);
        const auto* begin = static_cast<const double*>(info.ptr);
        database_.assign(begin, begin + vector_count_ * dimension_);
    }

    std::pair<std::size_t, double> find(
        const py::array_t<double, py::array::c_style | py::array::forcecast>& input) const {
        const py::buffer_info info = input.request();
        if (info.ndim != 1 || static_cast<std::size_t>(info.shape[0]) != dimension_) {
            throw py::value_error("query dimension does not match native index");
        }
        const auto* query = static_cast<const double*>(info.ptr);
        std::pair<std::size_t, double> result;
        {
            py::gil_scoped_release release;
            result = search(database_.data(), vector_count_, dimension_, query);
        }
        return result;
    }

    std::size_t vector_count() const { return vector_count_; }
    std::size_t dimension() const { return dimension_; }

  private:
    std::vector<double> database_;
    std::size_t vector_count_ = 0;
    std::size_t dimension_ = 0;
};

}  // namespace

PYBIND11_MODULE(case_b_native, module) {
    module.doc() = "Case B native vector search with explicit conversion-inclusive and reusable-index paths";
    module.def("find_nearest_copy", &find_nearest_copy, py::arg("database"), py::arg("query"));
    py::class_<NativeIndex>(module, "NativeIndex")
        .def(py::init<const py::array_t<double, py::array::c_style | py::array::forcecast>&>())
        .def("find", &NativeIndex::find)
        .def_property_readonly("vector_count", &NativeIndex::vector_count)
        .def_property_readonly("dimension", &NativeIndex::dimension);
}
