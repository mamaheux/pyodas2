#include <sstream>

#include <odas2/systems/mvdr.h>

#include "mvdr.h"

namespace py = pybind11;

struct mvdr_deleter {
    void operator()(mvdr_t* p) const {
        mvdr_destroy(p);
    }
};

std::shared_ptr<mvdr_t> mvdr_init(size_t num_channels, size_t num_bins) {
    return {mvdr_construct(num_channels, num_bins), mvdr_deleter()};
}

void mvdr_process_python(mvdr_t& self, const covs_t& covs, weights_t& coeffs) {
    if (coeffs.num_sources != 1) {
        throw py::value_error("The number of sources of the weights must be 1.");
    }
    if (self.num_channels != covs.num_channels) {
        throw py::value_error("The number of channels of the covs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != coeffs.num_channels) {
        throw py::value_error("The number of channels of the weights must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_bins != covs.num_bins) {
        throw py::value_error("The number of bins of the covs must be " + std::to_string(self.num_bins) + ".");
    }
    if (self.num_bins != coeffs.num_bins) {
        throw py::value_error("The number of bins of the weights must be " + std::to_string(self.num_bins) + ".");
    }

    if (mvdr_process(&self, &covs, &coeffs) != 0) {
        throw std::runtime_error("Failed to process mvdr");
    }
}

std::string mvdr_to_repr(const mvdr_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Mvdr (C=" << self.num_channels << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_mvdr(py::module& m) {
    py::class_<mvdr_t, std::shared_ptr<mvdr_t>>(m, "Mvdr", R"pbdoc(A class representing the mvdr process.)pbdoc")
        .def(py::init(&mvdr_init), R"pbdoc(Create a mvdr process.)pbdoc", py::arg("num_sources"), py::arg("num_bins"))
        .def_readonly("num_channels", &mvdr_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &mvdr_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &mvdr_process_python, R"pbdoc(Perform the mvdr process.)pbdoc", py::arg("covs"), py::arg("coeffs"))
        .def("__repr__", &mvdr_to_repr);
}
