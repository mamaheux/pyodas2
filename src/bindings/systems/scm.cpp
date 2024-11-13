#include <sstream>

#include <odas2/systems/scm.h>

#include "scm.h"

namespace py = pybind11;

struct scm_deleter {
    void operator()(scm_t* p) const {
        scm_destroy(p);
    }
};

std::shared_ptr<scm_t> scm_init(size_t num_channels, size_t num_bins, float alpha) {
    return {scm_construct(num_channels, num_bins, alpha), scm_deleter()};
}

void scm_process_python(scm_t& self, const freqs_t& freqs, const masks_t& masks, covs_t& covs) {
    if (self.num_channels != freqs.num_channels) {
        throw py::value_error("The number of channels of freqs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != masks.num_channels) {
        throw py::value_error("The number of channels of masks must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != covs.num_channels) {
        throw py::value_error("The number of channels of covs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_bins != freqs.num_bins) {
        throw py::value_error("The number of bins of freqs must be " + std::to_string(self.num_bins) + ".");
    }
    if (self.num_bins != masks.num_bins) {
        throw py::value_error("The number of bins of masks must be " + std::to_string(self.num_bins) + ".");
    }
    if (self.num_bins != covs.num_bins) {
        throw py::value_error("The number of bins of covs must be " + std::to_string(self.num_bins) + ".");
    }

    if (scm_process(&self, &freqs, &masks, &covs) != 0) {
        throw std::runtime_error("Failed to process scm");
    }
}

std::string scm_to_repr(const scm_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Scm (C=" << self.num_channels << ", B=" << self.num_bins << ", A=" << self.alpha << ")>";

    return ss.str();
}

void init_scm(py::module& m) {
    py::class_<scm_t, std::shared_ptr<scm_t>>(m, "Scm", R"pbdoc(A class representing the scm process.)pbdoc")
        .def(py::init(&scm_init), R"pbdoc(Create a scm process.)pbdoc", py::arg("num_channels"), py::arg("num_bins"), py::arg("alpha"))
        .def_readonly("num_channels", &scm_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &scm_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &scm_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def_readonly("alpha", &scm_t::alpha, R"pbdoc(Get the value of alpha.)pbdoc")
        .def("process", &scm_process_python, R"pbdoc(Perform the scm process.)pbdoc", py::arg("freqs"), py::arg("masks"), py::arg("covs"))
        .def("__repr__", &scm_to_repr);
}
