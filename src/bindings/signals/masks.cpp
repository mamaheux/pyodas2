#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/masks.h>

#include "masks.h"

namespace py = pybind11;

struct masks_deleter {
    void operator()(masks_t* p) const {
        masks_destroy(p);
    }
};

std::shared_ptr<masks_t> masks_init(const std::string& label, size_t num_channels, size_t num_bins) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(masks_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {masks_construct(label.c_str(), num_channels, num_bins), masks_deleter()};
}

void masks_load_numpy(masks_t& self, const py::array_t<float, py::array::c_style | py::array::forcecast>& array) {
    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_bins) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_bins) + ").");
    }

    size_t size = self.num_channels * self.num_bins;
    memcpy(self.gains_buffer, array.data(), size * sizeof(float));
}

py::array_t<float> masks_to_numpy(const masks_t& self) {
    py::buffer_info buffer_info(
        self.gains_buffer,
        sizeof(float),
        py::format_descriptor<float>::format(),
        2,  // Number of dimensions
        {self.num_channels, self.num_bins},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_bins * sizeof(float), sizeof(float)},
        true);  // Readonly

    return py::array_t<float>(buffer_info);
}

std::string masks_to_repr(const masks_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Masks (" << self.label << ", C=" << self.num_channels << ", B=" << self.num_bins << ")>";
    return ss.str();
}

void init_masks(py::module& m) {
    py::class_<masks_t, std::shared_ptr<masks_t>>(m, "Masks", R"pbdoc(A class representing a masks signal.)pbdoc")
        .def(py::init(&masks_init), R"pbdoc(Create a masks signal.)pbdoc", py::arg("label"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("label", &masks_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_channels", &masks_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_bins", &masks_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("load_numpy", &masks_load_numpy, R"pbdoc(Load the masks signal from a numpy array.)pbdoc", py::arg("array"))
        .def("to_numpy", &masks_to_numpy, R"pbdoc(Get the masks signal as a numpy array.)pbdoc")
        .def("__repr__", &masks_to_repr);
}
