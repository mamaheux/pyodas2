#include <sstream>

#include <odas2/systems/sst.h>

#include "sst.h"
#include "../utils/mics.h"

namespace py = pybind11;

struct sst_deleter {
    void operator()(sst_t* p) const {
        sst_destroy(p);
    }
};

std::shared_ptr<sst_t> sst_init(size_t num_tracks, size_t num_directions, size_t num_pasts) {
    return {sst_construct(num_tracks, num_directions, num_pasts), sst_deleter()};
}

void sst_process_python(sst_t& self, const dsf_t& dsf, const doas_t& in, doas_t& out) {
    if (self.num_directions != in.num_directions) {
        throw py::value_error("The number of directions of the input must be " + std::to_string(self.num_directions) + ".");
    }
    if (self.num_tracks != out.num_directions) {
        throw py::value_error("The number of directions of the output must be " + std::to_string(self.num_tracks) + ".");
    }

    if (sst_process(&self, &dsf, &in, &out) != 0) {
        throw std::runtime_error("Failed to process ssl");
    }
}

std::string sst_to_repr(const sst_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Sst (T=" << self.num_tracks << ", D=" << self.num_directions;
    ss << ", P=" << self.num_pasts << ")>";

    return ss.str();
}

void init_sst(py::module& m) {
    py::class_<sst_t, std::shared_ptr<sst_t>>(m, "Sst", R"pbdoc(A class representing the sst process.)pbdoc")
        .def(py::init(&sst_init), R"pbdoc(Create a sst process.)pbdoc", py::arg("num_tracks"), py::arg("num_directions"), py::arg("num_pasts"))
        .def_readonly("num_tracks", &sst_t::num_tracks, R"pbdoc(Get the number of tracks.)pbdoc")
        .def_readonly("num_directions", &sst_t::num_directions, R"pbdoc(Get the number of directions.)pbdoc")
        .def_readonly("num_pasts", &sst_t::num_pasts, R"pbdoc(Get the delta time.)pbdoc")
        .def("process", &sst_process_python, R"pbdoc(Perform the sst process.)pbdoc", py::arg("dsf"), py::arg("in"), py::arg("out"))
        .def("__repr__", &sst_to_repr);
}
