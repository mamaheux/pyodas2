#include <sstream>

#include <odas2/systems/phat.h>

#include "phat.h"

namespace py = pybind11;

struct phat_deleter {
    void operator()(phat_t* p) const {
        phat_destroy(p);
    }
};

std::shared_ptr<phat_t> phat_init(size_t num_channels, size_t num_bins) {
    return {phat_construct(num_channels, num_bins), phat_deleter()};
}

void phat_process_python(phat_t& self, const covs_t& covs_in, covs_t& covs_out) {
    if (self.num_channels != covs_in.num_channels) {
        throw py::value_error("The number of channels of the input must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != covs_out.num_channels) {
        throw py::value_error("The number of channels of the output must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_bins != covs_in.num_bins) {
        throw py::value_error("The number of bins of the input must be " + std::to_string(self.num_bins) + ".");
    }
    if (self.num_bins != covs_out.num_bins) {
        throw py::value_error("The number of bins of the output must be " + std::to_string(self.num_bins) + ".");
    }

    if (phat_process(&self, &covs_in, &covs_out) != 0) {
        throw std::runtime_error("Failed to process phat");
    }
}

std::string phat_to_repr(const phat_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Phat (C=" << self.num_channels << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_phat(py::module& m) {
    py::class_<phat_t, std::shared_ptr<phat_t>>(m, "Phat", R"pbdoc(A class representing the phat process.)pbdoc")
        .def(py::init(&phat_init), R"pbdoc(Create a phat process.)pbdoc", py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("num_channels", &phat_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &phat_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &phat_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &phat_process_python, R"pbdoc(Perform the phat process.)pbdoc", py::arg("covs_in"), py::arg("covs_out"))
        .def("__repr__", &phat_to_repr);
}
