#include <vector>
#include <sstream>

#include <pybind11/stl.h>

#include <odas2/systems/mixer.h>

#include "mixer.h"

namespace py = pybind11;

struct mixer_deleter {
    void operator()(mixer_t* p) const {
        mixer_destroy(p);
    }
};

std::shared_ptr<mixer_t> mixer_init(const std::vector<size_t>& mapping) {
    std::stringstream ss;

    for (size_t i = 0; i < mapping.size(); ++i) {
        ss << mapping[i];
        if (i < mapping.size() - 1) {
            ss << ',';
        }
    }

    return {mixer_construct(ss.str().c_str()), mixer_deleter()};
}

void mixer_process_python(mixer_t& self, const hops_t& hops_in, hops_t& hops_out) {
    if (self.max_map_index >= hops_in.num_channels) {
        throw py::value_error("hops_in does not have enough channels.");
    }
    if (self.num_channels != hops_out.num_channels) {
        throw py::value_error("hops_out does not have the same number of channels as the mixer.");
    }

    mixer_process(&self, &hops_in, &hops_out);
}

std::string mixer_to_repr(const mixer_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Mixer (C=" << self.num_channels << ")>";

    return ss.str();
}

void init_mixer(py::module& m) {
    py::class_<mixer_t, std::shared_ptr<mixer_t>>(m, "Mixer", R"pbdoc(A class representing the mixer process.)pbdoc")
        .def(py::init(&mixer_init), R"pbdoc(Create a mixer process.)pbdoc", py::arg("mapping"))
        .def_readonly("num_channels", &mixer_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def("process", &mixer_process_python, R"pbdoc(Perform the mixer process.)pbdoc", py::arg("hops_in"), py::arg("hops_out"))
        .def("__repr__", &mixer_to_repr);
}
