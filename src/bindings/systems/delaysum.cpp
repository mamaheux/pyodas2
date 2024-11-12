#include <sstream>

#include <odas2/systems/delaysum.h>

#include "delaysum.h"

namespace py = pybind11;

struct delaysum_deleter {
    void operator()(delaysum_t* p) const {
        delaysum_destroy(p);
    }
};

std::shared_ptr<delaysum_t> delaysum_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    return {delaysum_construct(num_sources, num_channels, num_bins), delaysum_deleter()};
}

void delaysum_process_python(delaysum_t& self, const tdoas_t& tdoas, weights_t& coeffs) {
    if (self.num_sources != tdoas.num_sources) {
        throw py::value_error("The number of sources of the tdoas must be " + std::to_string(self.num_sources) + ".");
    }
    if (self.num_sources != coeffs.num_sources) {
        throw py::value_error("The number of sources of the weights must be " + std::to_string(self.num_sources) + ".");
    }
    if (self.num_channels != tdoas.num_channels) {
        throw py::value_error("The number of channels of the tdoas must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != coeffs.num_channels) {
        throw py::value_error("The number of channels of the weights must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_bins != coeffs.num_bins) {
        throw py::value_error("The number of bins of the weights must be " + std::to_string(self.num_bins) + ".");
    }

    if (delaysum_process(&self, &tdoas, &coeffs) != 0) {
        throw std::runtime_error("Failed to process delaysum");
    }
}

std::string delaysum_to_repr(const delaysum_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.DelaySum (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_delaysum(py::module& m) {
    py::class_<delaysum_t, std::shared_ptr<delaysum_t>>(m, "DelaySum", R"pbdoc(A class representing the delaysum process.)pbdoc")
        .def(py::init(&delaysum_init), R"pbdoc(Create a delaysum process.)pbdoc", py::arg("num_sources"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("num_sources", &delaysum_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &delaysum_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &delaysum_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &delaysum_process_python, R"pbdoc(Perform the delaysum process.)pbdoc", py::arg("tdoas"), py::arg("coeffs"))
        .def("__repr__", &delaysum_to_repr);
}
