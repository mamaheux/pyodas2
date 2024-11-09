#include <pybind11/pybind11.h>

#include "types/xyz.h"
#include "utils/mic.h"
#include "utils/mics.h"
#include "utils/points.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
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
