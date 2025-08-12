#include <memory>
#include <sstream>

#include <odas2/utils/points.h>

#include "points.h"
#include "error.h"

namespace py = pybind11;

struct points_deleter {
    void operator()(points_t* p) const {
        points_destroy(p);
    }
};

std::shared_ptr<points_t> points_init(points_geometry_t geometry, size_t num_points) {
    points_t* points = points_construct(geometry, num_points);
    if (points == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {points, points_deleter()};
}

size_t points_len(const points_t& self) {
    return self.num_points;
}

xyz_t points_get_item(const points_t& self, size_t i) {
    if (i >= self.num_points) {
        throw py::index_error();
    }
    return self.points[i];
}

std::string points_to_repr(const points_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.utils.Points (len=" << self.num_points << ")>";
    return ss.str();
}

void init_points(py::module& m)
{
    py::class_<points_t, std::shared_ptr<points_t>> points(m,
        "Points",
        R"pbdoc(A class representing a geometry and containing an array of points.)pbdoc");

    py::enum_<points_geometry_t>(points, "Geometry")
        .value("SPHERE", POINTS_GEOMETRY_SPHERE)
        .value("HALFSPHERE", POINTS_GEOMETRY_HALFSPHERE)
        .value("CIRCLE", POINTS_GEOMETRY_CIRCLE)
        .value("ARC", POINTS_GEOMETRY_ARC);

    points.def(py::init(&points_init),
            R"pbdoc(
            Create the points for a given geometry.

            :param geometry: The geometry type.
            :param num_points: The number of points.)pbdoc",
            py::arg("geometry"),
            py::arg("num_points"))
        .def("__len__", &points_len, R"pbdoc(Get the number of points.)pbdoc")
        .def("__getitem__",
            &points_get_item,
            R"pbdoc(
            Get the immutable point at the given index.

            :param index: The index at which to return the point.)pbdoc",
            py::arg("index"))
        .def("__repr__", &points_to_repr);
}
