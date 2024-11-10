#include <complex>
#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/covs.h>

#include "covs.h"

namespace py = pybind11;

struct covs_deleter {
    void operator()(covs_t* p) const {
        covs_destroy(p);
    }
};

std::shared_ptr<covs_t> covs_init(const std::string& label, size_t num_channels, size_t num_bins) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(covs_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {covs_construct(label.c_str(), num_channels, num_bins), covs_deleter()};
}

void covs_xcorrs_load_numpy(const covs_t& self, const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& array) {
    if (array.ndim() != 2 || array.shape(0) != self.num_pairs || array.shape(1) != self.num_bins) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_bins) + ").");
    }

    size_t size = self.num_pairs * self.num_bins;
    memcpy(self.xcorrs_buffer, array.data(), size * sizeof(cplx_t));
}

py::array_t<std::complex<float>> covs_xcorrs_to_numpy(const covs_t& self) {
    py::buffer_info buffer_info(
        self.xcorrs_buffer,
        sizeof(std::complex<float>),
        py::format_descriptor<std::complex<float>>::format(),
        2,  // Number of dimensions
        {self.num_pairs, self.num_bins},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_bins * sizeof(cplx_t), sizeof(cplx_t)},
        true);  // Readonly

    return py::array_t<uint8_t>(buffer_info);
}

void covs_acorrs_load_numpy(const covs_t& self, const py::array_t<float, py::array::c_style | py::array::forcecast>& array) {
    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_bins) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_bins) + ").");
    }

    size_t size = self.num_channels * self.num_bins;
    memcpy(self.acorrs_buffer, array.data(), size * sizeof(float));
}

py::array_t<float> covs_acorrs_to_numpy(const covs_t& self) {
    py::buffer_info buffer_info(
        self.acorrs_buffer,
        sizeof(float),
        py::format_descriptor<float>::format(),
        2,  // Number of dimensions
        {self.num_channels, self.num_bins},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_bins * sizeof(float), sizeof(float)},
        true);  // Readonly

    return py::array_t<uint8_t>(buffer_info);
}

std::string covs_to_repr(const covs_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Covs (" << self.label << ", C=" << self.num_channels << ", P=" << self.num_pairs << ", B=" << self.num_bins << ")>";
    return ss.str();
}

void init_covs(py::module& m) {
    py::class_<covs_t, std::shared_ptr<covs_t>>(m, "Covs", R"pbdoc(A class representing a freqs signals.)pbdoc")
        .def(py::init(&covs_init), R"pbdoc(Create the hops signals.)pbdoc", py::arg("label"), py::arg("num_channels"), py::arg("num_bins"))
        .def_readonly("label", &covs_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_channels", &covs_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &covs_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &covs_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("xcorrs_load_numpy", &covs_xcorrs_load_numpy, R"pbdoc(Load the cross-correlation terms from a numpy array.)pbdoc", py::arg("array"))
        .def("xcorrs_to_numpy", &covs_xcorrs_to_numpy, R"pbdoc(Get the cross-correlation terms as a numpy array.)pbdoc")
        .def("acorrs_load_numpy", &covs_acorrs_load_numpy, R"pbdoc(Load the auto-correlation terms from a numpy array.)pbdoc", py::arg("array"))
        .def("acorrs_to_numpy", &covs_acorrs_to_numpy, R"pbdoc(Get the auto-correlation terms as a numpy array.)pbdoc")
        .def("__repr__", &covs_to_repr);
}
