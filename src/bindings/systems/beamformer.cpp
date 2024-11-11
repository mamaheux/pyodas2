#include <sstream>

#include <odas2/systems/beamformer.h>

#include "beamformer.h"

namespace py = pybind11;

struct beamformer_deleter {
    void operator()(beamformer_t* p) const {
        beamformer_destroy(p);
    }
};

std::shared_ptr<beamformer_t> beamformer_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    return {beamformer_construct(num_sources, num_channels, num_bins), beamformer_deleter()};
}

void beamformer_process_python(beamformer_t& self, const freqs_t& in, const weights_t& weights, freqs_t& out) {
    if (self.num_sources != weights.num_sources || self.num_sources != out.num_channels) {
        throw py::value_error("The number of sources does not match.");
    }
    if (self.num_channels != in.num_channels || self.num_channels != weights.num_channels) {
        throw py::value_error("The number of channels does not match.");
        }
    if (self.num_bins != in.num_bins ||
            self.num_bins != weights.num_bins ||
            self.num_bins != out.num_bins ) {
        throw py::value_error("The number of bins does not match.");
    }


    if (beamformer_process(&self, &in, &weights, &out) != 0) {
        throw std::runtime_error("Failed to process beamformer");
    }
}

std::string beamformer_to_repr(const beamformer_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Beamformer (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_beamformer(py::module& m) {
    py::class_<beamformer_t, std::shared_ptr<beamformer_t>>(m, "Beamformer", R"pbdoc(A class representing the beamformer process.)pbdoc")
        .def(py::init(&beamformer_init), R"pbdoc(Create a beamformer process.)pbdoc", py::arg("num_sources"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("num_sources", &beamformer_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &beamformer_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &beamformer_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &beamformer_process_python, R"pbdoc(Perform the beamformer process.)pbdoc", py::arg("in"), py::arg("weights"), py::arg("out"))
        .def("__repr__", &beamformer_to_repr);
}
