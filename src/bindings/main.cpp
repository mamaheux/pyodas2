#include <pybind11/pybind11.h>

#include "signals/covs.h"
#include "signals/doas.h"
#include "signals/freqs.h"
#include "signals/hops.h"
#include "signals/masks.h"
#include "signals/tdoas.h"
#include "signals/weights.h"

#include "systems/beamformer.h"
#include "systems/delaysum.h"
#include "systems/gcc.h"
#include "systems/mixer.h"
#include "systems/mvdr.h"
#include "systems/phat.h"
#include "systems/ssl.h"
#include "systems/steering.h"
#include "systems/stft.h"

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

    auto signals_module = m.def_submodule("signals");
    init_covs(signals_module);
    init_doas(signals_module);
    init_freqs(signals_module);
    init_hops(signals_module);
    init_masks(signals_module);
    init_tdoas(signals_module);
    init_weights(signals_module);

    auto systems_module = m.def_submodule("systems");
    init_beamformer(systems_module);
    init_delaysum(systems_module);
    init_gcc(systems_module);
    init_mixer(systems_module);
    init_mvdr(systems_module);
    init_phat(systems_module);
    init_ssl(systems_module);
    init_steering(systems_module);
    init_stft_istft(systems_module);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
