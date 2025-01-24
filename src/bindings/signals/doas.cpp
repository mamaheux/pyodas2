#include <sstream>

#include "doas.h"

namespace py = pybind11;

struct doas_deleter {
    void operator()(doas_t* p) const {
        doas_destroy(p);
    }
};

std::shared_ptr<doas_t> doas_init(const std::string& label, size_t num_directions) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(doas_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {doas_construct(label.c_str(), num_directions), doas_deleter()};
}

size_t doas_len(const doas_t& self) {
    return self.num_directions;
}

dir_t& doas_get_item(doas_t& self, size_t i) {
    if (i >= self.num_directions) {
        throw py::index_error();
    }
    return self.dirs[i];
}

void doas_set_item(doas_t& self, size_t i, dir_t direction) {
    if (i >= self.num_directions) {
        throw py::index_error();
    }
    self.dirs[i] = direction;
}

std::string doas_repr(const doas_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Doas (" << self.label << ", len=" << self.num_directions << ")>";

    return ss.str();
}

dir_t dir_init(src_t type, xyz_t coord, float energy, unsigned int tracking_id) {
    return {type, coord, energy, tracking_id};
}

dir_t dir_copy(const dir_t& self) {
    return self;
}

std::string dir_repr(const dir_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Doas.Dir ((" << self.coord.x << "," << self.coord.y << "," << self.coord.z << ")";
    ss << ", T=" << self.type << ", E=" << self.energy << ")>";

    return ss.str();
}

void init_doas(pybind11::module& m) {
    py::class_<doas_t, std::shared_ptr<doas_t>> doas(m,
        "Doas",
        R"pbdoc(A class representing an array of directions of arrival.)pbdoc");

    py::enum_<src_t>(doas, "Src", R"pbdoc(A enum representing the type of direction of arrival.)pbdoc")
        .value("UNDEFINED", UNDEFINED)
        .value("POTENTIAL", POTENTIAL)
        .value("TRACKED", TRACKED)
        .value("TARGET", TARGET);

    py::class_<dir_t>(doas, "Dir", R"pbdoc(A class representing a direction of arrival.)pbdoc")
        .def(py::init(&dir_init),
            R"pbdoc(
            Create a direction of arrival.

            :param type: The type of direction of arrival.
            :param coord: The direction of arrival represented by a 3D vector.
            :param energy: The energy of the direction of arrival.
            :param tracking_id: The tracking id of the direction of arrival (default is 0). )pbdoc",
            py::arg("type"),
            py::arg("coord"),
            py::arg("energy"),
            py::arg("tracking_id") = 0)
        .def_readwrite("type", &dir_t::type, R"pbdoc(Get/set the type of the direction of arrival.)pbdoc")
        .def_readwrite("coord", &dir_t::coord, R"pbdoc(Get/set the coord of the direction of arrival.)pbdoc")
        .def_readwrite("energy", &dir_t::energy, R"pbdoc(Get/set the energy of the direction of arrival.)pbdoc")
        .def_readwrite("tracking_id", &dir_t::tracking_id, R"pbdoc(Get/set the tracking id.)pbdoc")
        .def("copy", &dir_copy, R"pbdoc(Copy the direction of arrival.)pbdoc")
        .def("__repr__", &dir_repr);

    doas.def(py::init(&doas_init),
            R"pbdoc(
            Creates an array of directions of arrival.

            :param label: The label associated with the direction of arrival.
            :param num_directions: The number of directions of arrival in the array.
            )pbdoc",
            py::arg("label"),
            py::arg("num_directions"))
        .def_readonly("label", &doas_t::label, R"pbdoc(Get the label.)pbdoc")
        .def("__len__", &doas_len,  R"pbdoc(Get the number of directions of arrival.)pbdoc")
        .def("__getitem__",
            &doas_get_item,
            R"pbdoc(Get the mutable direction of arrival at the given index.

            :param index: The index at which to return the direction of arrival. )pbdoc",
            py::arg("index"),
            py::return_value_policy::reference)
        .def("__setitem__",
            &doas_set_item,
            R"pbdoc(
            Set the direction of arrival at the given index.

            :param index: The index at which the direction is assigned.
            :param direction: The direction of arrival to assign at the given index.)pbdoc",
            py::arg("index"),
            py::arg("direction"))
        .def("__repr__", &doas_repr);
}

void verify_doas_direction(const doas_t& doas) {
    for (size_t i = 0; i < doas.num_directions; i++) {
        float l2 = xyz_l2(doas.dirs[i].coord);
        if (fabsf(l2 - 1.f) > 1e-3 && l2 != 0.f) {
            throw py::value_error("All doas direction norms must be 1.");
        }
    }
}
