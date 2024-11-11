#include <complex>
#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/weights.h>

#include "weights.h"

namespace py = pybind11;

struct weights_deleter {
    void operator()(weights_t* p) const {
        weights_destroy(p);
    }
};

std::shared_ptr<weights_t> weights_init(const std::string& label, size_t num_sources, size_t num_channels, size_t num_bins) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(weights_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {weights_construct(label.c_str(), num_sources, num_channels, num_bins), weights_deleter()};
}

void weights_load_numpy(const weights_t& self, const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& array) {
    if (array.ndim() != 3 ||
        array.shape(0) != self.num_sources ||
        array.shape(1) != self.num_channels ||
        array.shape(2) != self.num_bins) {
        throw py::value_error("Invalid array shape, it must be (" +
            std::to_string(self.num_sources) + "," +
            std::to_string(self.num_channels) + "," +
            std::to_string(self.num_bins) + ").");
    }

    size_t size = self.num_sources * self.num_channels * self.num_bins;
    memcpy(self.bins_buffer, array.data(), size * sizeof(cplx_t));
}

py::array_t<std::complex<float>> weights_to_numpy(const weights_t& self) {
    py::buffer_info buffer_info(
        self.bins_buffer,
        sizeof(std::complex<float>),
        py::format_descriptor<std::complex<float>>::format(),
        3,  // Number of dimensions
        {self.num_sources, self.num_channels, self.num_bins},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_channels * self.num_bins * sizeof(cplx_t), self.num_bins * sizeof(cplx_t), sizeof(cplx_t)},
        true);  // Readonly

    return py::array_t<std::complex<float>>(buffer_info);
}

std::string weights_to_repr(const weights_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Weights (" << self.label;
    ss << ", S=" << self.num_sources << ", C=" << self.num_channels << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_weights(py::module& m) {
    py::class_<weights_t, std::shared_ptr<weights_t>>(m, "Weights", R"pbdoc(A class representing a weights signal.)pbdoc")
        .def(py::init(&weights_init), R"pbdoc(Create a weights signal.)pbdoc", py::arg("label"), py::arg("num_sources"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("label", &weights_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_sources", &weights_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &weights_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &weights_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("load_numpy", &weights_load_numpy, R"pbdoc(Load the weights signal from a numpy array.)pbdoc", py::arg("array"))
        .def("to_numpy", &weights_to_numpy, R"pbdoc(Get the weights signal as a numpy array.)pbdoc")
        .def("__repr__", &weights_to_repr);
}
