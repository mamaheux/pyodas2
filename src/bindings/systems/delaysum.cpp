#include <sstream>

#include <odas2/systems/delaysum.h>

#include "delaysum.h"
#include "../utils/error.h"

namespace py = pybind11;

struct delaysum_deleter {
    void operator()(delaysum_t* p) const {
        delaysum_destroy(p);
    }
};

std::shared_ptr<delaysum_t> delaysum_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    delaysum_t* delaysum = delaysum_construct(num_sources, num_channels, num_bins);
    if (delaysum == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {delaysum, delaysum_deleter()};
}

void delaysum_process_python(delaysum_t& self, const tdoas_t& tdoas, weights_t& coeffs) {
    if (delaysum_process(&self, &tdoas, &coeffs) != 0) {
        throw py::value_error(pyodas2_error_message());
    }
}

std::string delaysum_to_repr(const delaysum_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.DelaySum (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_delaysum(py::module& m) {
    py::class_<delaysum_t, std::shared_ptr<delaysum_t>>(m,
            "DelaySum",
            R"pbdoc(A class for the delay and sum beamformer..)pbdoc")
        .def(py::init(&delaysum_init),
            R"pbdoc(
            Create a DelaySum instance.

            :param num_sources: The number of audio sources, the number of time differences of arrival.
            :param num_channels: The number of channels.
            :param num_bins: The number of frequency bins.)pbdoc",
            py::arg("num_sources"),
            py::arg("num_channels"),
            py::arg("num_bins"))
        .def_readonly("num_sources", &delaysum_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &delaysum_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &delaysum_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process",
            &delaysum_process_python,
            R"pbdoc(
            Perform the delay and sum beamformer process. The argument parameters must match those of the instance.

            :param tdoas: The input time differences of arrival.
            :param coeffs: The computed beamformer coefficients.)pbdoc",
            py::arg("tdoas"),
            py::arg("coeffs"))
        .def("__repr__", &delaysum_to_repr);
}
