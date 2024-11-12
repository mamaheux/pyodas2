#include <sstream>

#include <odas2/systems/gcc.h>

#include "gcc.h"

namespace py = pybind11;

struct gcc_deleter {
    void operator()(gcc_t* p) const {
        gcc_destroy(p);
    }
};

std::shared_ptr<gcc_t> gcc_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    float num_samples = static_cast<float>(num_bins - 1) * 2;
    if (ceilf(log2f(num_samples)) != floorf(log2f(num_samples))) {
        throw py::value_error("The number of samples must be a power of 2 and the number of bins must be (num_samples / 2) + 1.");
    }

    return {gcc_construct(num_sources, num_channels, num_bins), gcc_deleter()};
}

void gcc_process_python(gcc_t& self, const covs_t& covs, tdoas_t& tdoas) {
    if (self.num_sources != tdoas.num_sources) {
        throw py::value_error("The number of sources of the tdoas must be " + std::to_string(self.num_sources) + ".");
    }
    if (self.num_channels != covs.num_channels) {
        throw py::value_error("The number of channels of the covs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != tdoas.num_channels) {
        throw py::value_error("The number of channels of the tdoas must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_bins != covs.num_bins) {
        throw py::value_error("The number of bins of the covs must be " + std::to_string(self.num_bins) + ".");
    }

    if (gcc_process(&self, &covs, &tdoas) != 0) {
        throw std::runtime_error("Failed to process gcc");
    }
}

std::string gcc_to_repr(const gcc_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Gcc (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_gcc(py::module& m) {
    py::class_<gcc_t, std::shared_ptr<gcc_t>>(m, "Gcc", R"pbdoc(A class representing the gcc process.)pbdoc")
        .def(py::init(&gcc_init), R"pbdoc(Create a gcc process.)pbdoc", py::arg("num_sources"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("num_sources", &gcc_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &gcc_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &gcc_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &gcc_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def_readonly("num_samples", &gcc_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("interpolation_factor", &gcc_t::interpolation_factor, R"pbdoc(Get the interpolation factor.)pbdoc")
        .def("process", &gcc_process_python, R"pbdoc(Perform the gcc process.)pbdoc", py::arg("covs"), py::arg("tdoas"))
        .def("__repr__", &gcc_to_repr);
}
