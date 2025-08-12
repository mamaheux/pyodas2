#include <sstream>

#include <odas2/systems/mvdr.h>

#include "mvdr.h"
#include "../utils/error.h"

namespace py = pybind11;

struct mvdr_deleter {
    void operator()(mvdr_t* p) const {
        mvdr_destroy(p);
    }
};

std::shared_ptr<mvdr_t> mvdr_init(size_t num_channels, size_t num_bins) {
    mvdr_t* mvdr = mvdr_construct(num_channels, num_bins);
    if (mvdr == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {mvdr, mvdr_deleter()};
}

void mvdr_process_python(mvdr_t& self, const covs_t& covs, weights_t& coeffs) {
    if (mvdr_process(&self, &covs, &coeffs) != 0) {
        throw py::value_error(pyodas2_error_message());
    }
}

std::string mvdr_to_repr(const mvdr_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Mvdr (C=" << self.num_channels << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_mvdr(py::module& m) {
    py::class_<mvdr_t, std::shared_ptr<mvdr_t>>(m,
            "Mvdr",
            R"pbdoc(A class for the minimum variance distortionless response (MVDR) beamformer.)pbdoc")
        .def(py::init(&mvdr_init),
            R"pbdoc(
            Create a Mvdr instance.

            :param num_channels: The number of channels.
            :param num_bins: The number of frequency bins.)pbdoc",
            py::arg("num_sources"),
            py::arg("num_bins"))
        .def_readonly("num_channels", &mvdr_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &mvdr_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process",
            &mvdr_process_python,
            R"pbdoc(
            Perform the minimum variance distortionless response (MVDR) beamformer process.
            The argument parameters must match those of the instance.

            :param covs: The input covariance matrix.
            :param coeffs: The computed beamformer coefficients.)pbdoc",
            py::arg("covs"),
            py::arg("coeffs"))
        .def("__repr__", &mvdr_to_repr);
}
