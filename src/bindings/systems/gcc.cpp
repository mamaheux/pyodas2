#include <sstream>

#include <odas2/systems/gcc.h>

#include "gcc.h"
#include "../utils/error.h"

namespace py = pybind11;

struct gcc_deleter {
    void operator()(gcc_t* p) const {
        gcc_destroy(p);
    }
};

std::shared_ptr<gcc_t> gcc_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    gcc_t* gcc = gcc_construct(num_sources, num_channels, num_bins);
    if (gcc == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {gcc, gcc_deleter()};
}

void gcc_process_python(gcc_t& self, const covs_t& covs, tdoas_t& tdoas) {
    if (gcc_process(&self, &covs, &tdoas) != 0) {
        throw py::value_error(pyodas2_error_message());
    }
}

std::string gcc_to_repr(const gcc_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Gcc (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_gcc(py::module& m) {
    py::class_<gcc_t, std::shared_ptr<gcc_t>>(m,
            "Gcc",
            R"pbdoc(A class computing the generalized cross-correlation.)pbdoc")
        .def(py::init(&gcc_init),
            R"pbdoc(
            Create a Gcc instance.

            :param num_sources: The number of audio source, the number of time differences of arrival candidates.
            :param num_channels: The number of channels.
            :param num_bins: The number of frequency bins.)pbdoc",
            py::arg("num_sources"),
            py::arg("num_channels"),
            py::arg("num_bins"))
        .def_readonly("num_sources", &gcc_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &gcc_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &gcc_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &gcc_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def_readonly("num_samples", &gcc_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("interpolation_factor", &gcc_t::interpolation_factor, R"pbdoc(Get the interpolation factor.)pbdoc")
        .def("process",
            &gcc_process_python,
            R"pbdoc(
            Perform the gcc process. The argument parameters must match those of the instance.

            :param covs: The spatial covariance matrix.
            :param tdoas: The computed time differences of arrival candidates.)pbdoc",
            py::arg("covs"),
            py::arg("tdoas"))
        .def("__repr__", &gcc_to_repr);
}
