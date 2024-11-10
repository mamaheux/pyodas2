#include <complex>
#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/freqs.h>

#include "freqs.h"

namespace py = pybind11;

struct freqs_deleter {
    void operator()(freqs_t* p) const {
        freqs_destroy(p);
    }
};

std::shared_ptr<freqs_t> freqs_init(const std::string& label, size_t num_channels, size_t num_bins) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(freqs_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {freqs_construct(label.c_str(), num_channels, num_bins), freqs_deleter()};
}

void freqs_load_numpy(const freqs_t& self, const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& array) {
    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_bins) {
        throw py::value_error("Invalid array shape. It must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_bins) + ").");
    }

    size_t size = self.num_channels * self.num_bins;
    memcpy(self.bins_buffer, array.data(), size * sizeof(cplx_t));
}

py::array_t<std::complex<float>> freqs_to_numpy(const freqs_t& self) {
    py::buffer_info buffer_info(
        self.bins_buffer,
        sizeof(std::complex<float>),
        py::format_descriptor<std::complex<float>>::format(),
        2,  // Number of dimensions
        {self.num_channels, self.num_bins},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_bins * sizeof(cplx_t), sizeof(cplx_t)},
        true);  // Readonly

    return py::array_t<uint8_t>(buffer_info);
}

std::string freqs_to_repr(const freqs_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Freqs (" << self.label << ", C=" << self.num_channels << ", B=" << self.num_bins << ")>";
    return ss.str();
}

void init_freqs(py::module& m) {
    py::class_<freqs_t, std::shared_ptr<freqs_t>>(m, "Freqs", R"pbdoc(A class representing a freqs signals.)pbdoc")
        .def(py::init(&freqs_init), R"pbdoc(Create the hops signals.)pbdoc", py::arg("label"), py::arg("num_channels"), py::arg("num_shifts"))
        .def_readonly("label", &freqs_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_channels", &freqs_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &freqs_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("load_numpy", &freqs_load_numpy, R"pbdoc(Load the data of a numpy array.)pbdoc", py::arg("array"))
        .def("to_numpy", &freqs_to_numpy, R"pbdoc(Get the freqs signal as a numpy array.)pbdoc")
        .def("__repr__", &freqs_to_repr);
}
