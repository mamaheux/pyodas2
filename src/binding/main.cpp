#include <pybind11/pybind11.h>

#include "types/xyz.h"
#include "utils/mic.h"
#include "utils/mics.h"
#include "utils/points.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.attr("__name__") = "pyodas2"; // Remove ._core from the names

    auto types_module = m.def_submodule("types");
    init_xyz(types_module);

    auto utils_module = m.def_submodule("utils");
    init_mic(utils_module);
    init_mics(utils_module);
    init_points(utils_module);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
