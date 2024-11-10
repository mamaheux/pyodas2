#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/hops.h>

#include "hops.h"

namespace py = pybind11;

struct hops_deleter {
    void operator()(hops_t* p) const {
        hops_destroy(p);
    }
};

std::shared_ptr<hops_t> hops_init(const std::string& label, size_t num_channels, size_t num_shifts) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(hops_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {hops_construct(label.c_str(), num_channels, num_shifts), hops_deleter()};
}

template <class Int>
void hops_load_numpy_int(const hops_t& self, const py::array_t<Int, py::array::c_style>& array) {
    static_assert(std::is_integral_v<Int>, "Integral required.");
    static_assert(std::is_signed_v<Int>, "Signed required.");

    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_shifts) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_shifts) + ").");
    }

    size_t size = self.num_channels * self.num_shifts;
    for (size_t i = 0; i < size; i++) {
        self.samples_buffer[i] = -static_cast<float>(array.data()[i]) / std::numeric_limits<Int>::min();
    }
}

template <class UInt>
void hops_load_numpy_uint(const hops_t& self, const py::array_t<UInt, py::array::c_style>& array) {
    static_assert(std::is_integral_v<UInt>, "Integral required.");
    static_assert(std::is_unsigned_v<UInt>, "Unsigned required.");

    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_shifts) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_shifts) + ").");
    }

    size_t size = self.num_channels * self.num_shifts;
    for (size_t i = 0; i < size; i++) {
        constexpr float SCALE = 2.f / std::numeric_limits<UInt>::max();
        constexpr float OFFSET = 1.f;

        self.samples_buffer[i] = static_cast<float>(array.data()[i]) * SCALE - OFFSET;
    }
}

template <class Float>
void hops_load_numpy_float(const hops_t& self, const py::array_t<Float, py::array::c_style>& array) {
    static_assert(std::is_floating_point_v<Float>, "Floating point required.");

    if (array.ndim() != 2 || array.shape(0) != self.num_channels || array.shape(1) != self.num_shifts) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_channels) + "," + std::to_string(self.num_shifts) + ").");
    }

    size_t size = self.num_channels * self.num_shifts;
    for (size_t i = 0; i < size; i++) {
        self.samples_buffer[i] = static_cast<float>(array.data()[i]);
    }
}

py::array_t<float> hops_to_numpy(const hops_t& self) {
    py::buffer_info buffer_info(
        self.samples_buffer,
        sizeof(float),
        py::format_descriptor<float>::format(),
        2,  // Number of dimensions
        {self.num_channels, self.num_shifts},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_shifts * sizeof(float), sizeof(float)},
        true);  // Readonly

    return py::array_t<uint8_t>(buffer_info);
}

std::string hops_to_repr(const hops_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Hops (" << self.label << ", C=" << self.num_channels << ", S=" << self.num_shifts << ")>";
    return ss.str();
}

void init_hops(py::module& m) {
    py::class_<hops_t, std::shared_ptr<hops_t>>(m, "Hops", R"pbdoc(A class representing a hops signals.)pbdoc")
        .def(py::init(&hops_init), R"pbdoc(Create the hops signals.)pbdoc", py::arg("label"), py::arg("num_channels"), py::arg("num_shifts"))
        .def_readonly("label", &hops_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_channels", &hops_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_shifts", &hops_t::num_shifts, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("num_samples", &hops_t::num_shifts, R"pbdoc(Get the number of samples.)pbdoc")
        .def("load_numpy", &hops_load_numpy_int<int8_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_int<int16_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_int<int32_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_int<int64_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_uint<uint8_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_uint<uint16_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_uint<uint32_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_uint<uint64_t>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_float<float>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("load_numpy", &hops_load_numpy_float<double>, R"pbdoc(Load the hops signal from a numpy array.)pbdoc", py::arg("array"))
        .def("to_numpy", &hops_to_numpy, R"pbdoc(Get the hops signal as a numpy array.)pbdoc")
        .def("__repr__", &hops_to_repr);
}
