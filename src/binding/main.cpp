#include <pybind11/pybind11.h>

#include "signals/freqs.h"
#include "signals/hops.h"

#include "types/xyz.h"

#include "utils/mic.h"
#include "utils/mics.h"
#include "utils/points.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.attr("__name__") = "pyodas2"; // Remove ._core from the names

    auto signals_module = m.def_submodule("signals");
    init_freqs(signals_module);
    init_hops(signals_module);

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
