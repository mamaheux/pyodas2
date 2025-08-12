#include <complex>
#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/covs.h>

#include "covs.h"
#include "../utils/error.h"

namespace py = pybind11;

struct covs_deleter {
    void operator()(covs_t* p) const {
        covs_destroy(p);
    }
};

std::shared_ptr<covs_t> covs_init(const std::string& label, size_t num_channels, size_t num_bins) {
    covs_t* covs = covs_construct(label.c_str(), num_channels, num_bins);
    if (covs == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {covs, covs_deleter()};
}

void covs_xcorrs_load_numpy(covs_t& self, const py::array_t<std::complex<float>, py::array::c_style | py::array::forcecast>& array) {
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

    return py::array_t<std::complex<float>>(buffer_info);
}

void covs_acorrs_load_numpy(covs_t& self, const py::array_t<float, py::array::c_style | py::array::forcecast>& array) {
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

    return py::array_t<float>(buffer_info);
}

std::string covs_to_repr(const covs_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Covs (" << self.label << ", C=" << self.num_channels << ", P=" << self.num_pairs << ", B=" << self.num_bins << ")>";
    return ss.str();
}

void init_covs(py::module& m) {
    py::class_<covs_t, std::shared_ptr<covs_t>>(m,
            "Covs",
            R"pbdoc(A class representing a spatial covariance matrix represented by the autocorrelation and cross-correlation.
            For each microphone pair, the autocorrelation representes diagonal terms of each spatial covariance matrix.
            For each microphone pair, the cross-correlation for the upper triangle of each spatial covariance matrix.)pbdoc")
        .def(py::init(&covs_init),
            R"pbdoc(
            Create a spatial covariance matrix.

            :param label: The label associated with the spatial covariance matrix.
            :param num_channels: The number of channels.
            :param num_bins: The number of frequency bins.)pbdoc",
            py::arg("label"),
            py::arg("num_channels"),
            py::arg("num_bins"))
        .def_readonly("label", &covs_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_channels", &covs_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &covs_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_readonly("num_bins", &covs_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("xcorrs_load_numpy",
            &covs_xcorrs_load_numpy,
            R"pbdoc(
            Load the cross-correlation terms from a numpy array.

            :param xcorrs: The cross-correlation for each microphone pair of shape (num_pairs, num_bins).)pbdoc",
            py::arg("xcorrs"))
        .def("xcorrs_to_numpy",
            &covs_xcorrs_to_numpy,
            R"pbdoc(Get the cross-correlation terms as a numpy array of shape (num_pairs, num_bins).)pbdoc")
        .def("acorrs_load_numpy",
            &covs_acorrs_load_numpy,
            R"pbdoc(
            Load the autocorrelation terms from a numpy array.

            :param acorrs: The autocorrelation for each microphone of shape (num_channels, num_bins).)pbdoc",
            py::arg("acorrs"))
        .def("acorrs_to_numpy",
            &covs_acorrs_to_numpy,
            R"pbdoc(Get the autocorrelation terms as a numpy array of shape (num_channels, num_bins).)pbdoc")
        .def("__repr__", &covs_to_repr);
}
