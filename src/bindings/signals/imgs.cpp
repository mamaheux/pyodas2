#include <sstream>

#include <pybind11/numpy.h>

#include <odas2/signals/imgs.h>

#include "imgs.h"
#include "../utils/error.h"

namespace py = pybind11;

struct imgs_deleter {
    void operator()(imgs_t* p) const {
        imgs_destroy(p);
    }
};

std::shared_ptr<imgs_t> imgs_init(const std::string& label, size_t num_points, size_t num_directions) {
    imgs_t* imgs = imgs_construct(label.c_str(), num_points, num_directions);
    if (imgs == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {imgs, imgs_deleter()};
}

void imgs_load_numpy(imgs_t& self, const py::array_t<float, py::array::c_style>& array) {
    if (array.ndim() != 2 || array.shape(0) != self.num_directions || array.shape(1) != self.num_points) {
        throw py::value_error("Invalid array shape, it must be (" + std::to_string(self.num_directions) + "," + std::to_string(self.num_points) + ").");
    }

    size_t size = self.num_directions * self.num_points;
    for (size_t i = 0; i < size; i++) {
        self.energies_buffer[i] = array.data()[i];
    }
}

py::array_t<float> imgs_to_numpy(const imgs_t& self) {
    py::buffer_info buffer_info(
        self.energies_buffer,
        sizeof(float),
        py::format_descriptor<float>::format(),
        2,  // Number of dimensions
        {self.num_directions, self.num_points},  // Buffer dimensions
        // Strides (in bytes) for each index
        {self.num_points * sizeof(float), sizeof(float)},
        true);  // Readonly

    return py::array_t<float>(buffer_info);
}

std::string imgs_to_repr(const imgs_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.signals.Img (" << self.label << ", D=" << self.num_directions << ", P=" << self.num_points << ")>";
    return ss.str();
}

void init_imgs(py::module& m) {
    py::class_<imgs_t, std::shared_ptr<imgs_t>>(m,
            "Imgs",
            R"pbdoc(A class representing acoustic images )pbdoc")
        .def(py::init(&imgs_init),
            R"pbdoc(
            Create an Imgs instance.

            :param label: The label associated with the chunk of audio samples..
            :param num_points: The number of points.
            :param num_directions: The number of directions.)pbdoc",
            py::arg("label"),
            py::arg("num_points"),
            py::arg("num_directions"))
        .def_readonly("label", &imgs_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readonly("num_points", &imgs_t::num_points, R"pbdoc(Get the number of points.)pbdoc")
        .def_readonly("num_directions", &imgs_t::num_directions, R"pbdoc(Get the number of directions.)pbdoc")
        .def("load_numpy",
            &imgs_load_numpy,
            R"pbdoc(
            Load the imgs signal from a numpy array.

            :param array: The audio sample array of shape (num_directions, num_points).)pbdoc",
            py::arg("array"))
        .def("to_numpy",
            &imgs_to_numpy,
            R"pbdoc(Get the imgs signal as a numpy array of shape (num_directions, num_points).)pbdoc")
        .def("__repr__", &imgs_to_repr);
}
