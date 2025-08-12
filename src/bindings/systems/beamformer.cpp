#include <sstream>

#include <odas2/systems/beamformer.h>

#include "beamformer.h"
#include "../utils/error.h"

namespace py = pybind11;

struct beamformer_deleter {
    void operator()(beamformer_t* p) const {
        beamformer_destroy(p);
    }
};

std::shared_ptr<beamformer_t> beamformer_init(size_t num_sources, size_t num_channels, size_t num_bins) {
    beamformer_t* beamformer = beamformer_construct(num_sources, num_channels, num_bins);
    if (beamformer == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {beamformer, beamformer_deleter()};
}

void beamformer_process_python(beamformer_t& self, const freqs_t& in, const weights_t& weights, freqs_t& out) {
    if (beamformer_process(&self, &in, &weights, &out) != 0) {
        throw py::value_error(pyodas2_error_message());
    }
}

std::string beamformer_to_repr(const beamformer_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Beamformer (S=" << self.num_sources << ", C=" << self.num_channels;
    ss << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_beamformer(py::module& m) {
    py::class_<beamformer_t, std::shared_ptr<beamformer_t>>(m,
            "Beamformer",
            R"pbdoc(A class applying beamformer coefficients.)pbdoc")
        .def(py::init(&beamformer_init),
            R"pbdoc(
            Create a Beamformer instance.

            :param num_sources: The number of sources, the number of output channels.
            :param num_channels: The number of input channels.
            :param num_bins: The number of frequency bins.)pbdoc",
            py::arg("num_sources"),
            py::arg("num_channels"),
            py::arg("num_bins"))
        .def_readonly("num_sources", &beamformer_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &beamformer_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &beamformer_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process",
            &beamformer_process_python,
            R"pbdoc(
            Perform the beamformer process. The argument parameters must match those of the instance.

            :param in: The input signal in frequency domain.
            :param weights: The beamformer coefficients.
            :param out: The output signal in frequency domain.)pbdoc",
            py::arg("in"),
            py::arg("weights"),
            py::arg("out"))
        .def("__repr__", &beamformer_to_repr);
}
