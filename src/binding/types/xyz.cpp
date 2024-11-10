#include <sstream>

#include <pybind11/operators.h>

#include <odas2/types/xyz.h>

#include "xyz.h"

namespace py = pybind11;

xyz_t operator+(const xyz_t& a, const xyz_t& b) {
    return xyz_add(a, b);
}

xyz_t operator-(const xyz_t& a, const xyz_t& b) {
    return xyz_sub(a, b);
}

xyz_t operator*(const float& scale, const xyz_t& vec) {
    return xyz_scale(vec, scale);
}

xyz_t operator*(const xyz_t& vec, const float& scale) {
    return xyz_scale(vec, scale);
}

xyz_t operator-(const xyz_t& a) {
    return xyz_scale(a, -1.f);
}

std::string xyz_to_repr(const xyz_t& xyz) {
    std::stringstream ss;
    ss << "<pyodas2.types.Xyz (" << xyz.x << "," << xyz.y << "," << xyz.z << ")>";
    return ss.str();
}

std::string xyz_to_string(const xyz_t& xyz) {
    std::stringstream ss;
    ss << "(" << xyz.x << "," << xyz.y << "," << xyz.z << ")";
    return ss.str();
}

void init_xyz(py::module &m) {
    py::class_<xyz_t>(m, "Xyz", R"pbdoc(A class representing a 3D vector.)pbdoc")
        .def(py::init(&xyz_cst), R"pbdoc(Create a new xyz vector.)pbdoc", py::arg("x"), py::arg("y"), py::arg("z"))
        .def_readwrite("x", &xyz_t::x, R"pbdoc(X value of the vector.)pbdoc")
        .def_readwrite("y", &xyz_t::y, R"pbdoc(Y value of the vector.)pbdoc")
        .def_readwrite("z", &xyz_t::z, R"pbdoc(Z value of the vector.)pbdoc")
        .def("unit", &xyz_unit, R"pbdoc(Return the unit vector with the same direction of self.)pbdoc")
        .def("mag", &xyz_mag, R"pbdoc(Return the magnitude of the vector.)pbdoc")
        .def("l2", &xyz_l2, R"pbdoc(Return the square of the magnitude of the vector.)pbdoc")
        .def("dot", &xyz_dot, R"pbdoc(Return the dot product of the vectors.)pbdoc", py::arg("other"))
        .def("cross", &xyz_vec, R"pbdoc(Return the cross product of the vectors.)pbdoc", py::arg("other"))
        .def(py::self + py::self, R"pbdoc(Add two vectors.)pbdoc")
        .def(py::self - py::self, R"pbdoc(Add subtract two vectors.)pbdoc")
        .def(py::self * float(), R"pbdoc(Scale a vector.)pbdoc")
        .def(float() * py::self, R"pbdoc(Scale a vector.)pbdoc")
        .def(-py::self, R"pbdoc(Inverse a vector.)pbdoc")
        .def("__repr__", &xyz_to_repr)
        .def("__str__", &xyz_to_string);
}
