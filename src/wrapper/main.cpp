#include <pybind11/pybind11.h>

#include "types/xyz.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = R"pbdoc(
        Pyodas2 lib
        -----------------------

        .. currentmodule:: pyodas2

        .. autosummary::
           :toctree: _generate
    )pbdoc";

    auto types_module = m.def_submodule("types", R"pbdoc(
        Pyodas2 types submodule
        -----------------------

        .. currentmodule:: pyodas2.types

        .. autosummary::
           :toctree: _generate
    )pbdoc");
    init_xyz(types_module);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
