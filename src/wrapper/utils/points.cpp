#include <memory>
#include <sstream>

#include <odas2/utils/points.h>

#include "points.h"

namespace py = pybind11;

enum class Geometry {
    SPHERE,
    HALFSPHERE,
    ARC
};

struct points_deleter {
    void operator()(points_t* p) const     {
        points_destroy(p);
    }
};

std::shared_ptr<points_t> points_init(Geometry geometry) {
    switch (geometry) {
        case Geometry::SPHERE:
            return {points_construct("sphere"), points_deleter()};
        case Geometry::HALFSPHERE:
            return {points_construct("halfsphere"), points_deleter()};
        case Geometry::ARC:
            return {points_construct("arc"), points_deleter()};
        default:
            throw py::value_error("Not supported geometry");
    }
}

size_t points_len(const points_t& self) {
    return self.num_points;
}

xyz_t points_get_item(const points_t& self, size_t i) {
    if (i >= self.num_points) {
        throw std::out_of_range("");
    }
    return self.points[i];
}

void init_points(py::module& m)
{
    py::class_<points_t, std::shared_ptr<points_t>> points(m, "Points");
    points.def(py::init(&points_init), R"pbdoc(Create the points for a given geometry)pbdoc", py::arg("geometry"))
        .def("__len__", &points_len)
        .def("__getitem__", &points_get_item);

    py::enum_<Geometry>(points, "Geometry")
        .value("Sphere", Geometry::SPHERE)
        .value("Halfsphere", Geometry::HALFSPHERE)
        .value("Arc", Geometry::ARC);
}
