#include <sstream>

#include <odas2/signals/doas.h>

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

dir_t& doas_get_item(const doas_t& self, size_t i) {
    if (i >= self.num_directions) {
        throw py::index_error();
    }
    return self.dirs[i];
}

void doas_set_item(const doas_t& self, size_t i, dir_t direction) {
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

dir_t dir_init(src_t type, xyz_t coord, float energy) {
    return {type, coord, energy};
}

std::string dir_repr(const dir_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Doas.Dir ((" << self.coord.x << "," << self.coord.y << "," << self.coord.y << ")";
    ss << ", T=" << self.type << ", E=" << self.energy << ")>";

    return ss.str();
}

void init_doas(pybind11::module& m) {
    py::class_<doas_t, std::shared_ptr<doas_t>> doas(m, "Doas", R"pbdoc(A class representing an array of directions of arrival.)pbdoc");

    py::enum_<src_t>(doas, "Src", R"pbdoc(A enum representing the type of direction of arrival.)pbdoc")
        .value("UNDEFINED", UNDEFINED)
        .value("POTENTIAL", POTENTIAL)
        .value("TRACKED", TRACKED)
        .value("TARGET", TARGET);

    py::class_<dir_t>(doas, "Dir", R"pbdoc(A class representing a direction of arrival.)pbdoc")
        .def(py::init(&dir_init), R"pbdoc(Create a direction of arrival.)pbdoc", py::arg("type"), py::arg("coord"), py::arg("energy"))
        .def_readwrite("type", &dir_t::type, R"pbdoc(Get/set the type of the direction of arrival.)pbdoc")
        .def_readwrite("coord", &dir_t::coord, R"pbdoc(Get/set the coord of the direction of arrival.)pbdoc")
        .def_readwrite("energy", &dir_t::energy, R"pbdoc(Get/set the energy of the direction of arrival.)pbdoc")
        .def("__repr__", &dir_repr);

    doas.def(py::init(&doas_init), R"pbdoc(Create doas.)pbdoc", py::arg("label"), py::arg("num_directions"))
        .def_readonly("label", &doas_t::label, R"pbdoc(Get the label.)pbdoc")
        .def("__len__", &doas_len,  R"pbdoc(Get the number of directions of arrival.)pbdoc")
        .def("__getitem__", &doas_get_item, R"pbdoc(Get the mutable direction of arrival at the given index.)pbdoc", py::arg("index"), py::return_value_policy::reference)
        .def("__setitem__", &doas_set_item, R"pbdoc(Set the direction of arrival at the given index.)pbdoc", py::arg("index"), py::arg("direction"))
        .def("__repr__", &doas_repr);
}
