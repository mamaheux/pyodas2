#include <sstream>

#include <odas2/utils/mics.h>

#include "mic.h"

namespace py = pybind11;

enum class Pattern {
    OMNIDIRECTIONAL,
    CARDIOID,
};

mic_t mic_init(const xyz_t position, const xyz_t direction, Pattern pattern) {
    switch (pattern) {
        case Pattern::OMNIDIRECTIONAL:
            return mic_cst(position, direction, "omnidirectional");
        case Pattern::CARDIOID:
            return mic_cst(position, direction, "cardioid");
        default:
            throw py::value_error("Not supported pattern");
    }
}

Pattern mic_get_pattern(const mic_t& self) {
    if (strcmp(self.pattern, "omnidirectional") == 0) {
        return Pattern::OMNIDIRECTIONAL;
    }
    else if (strcmp(self.pattern, "cardioid") == 0) {
        return Pattern::CARDIOID;
    }
    else {
        throw py::value_error("Not supported pattern");
    }
}

void mic_set_pattern(mic_t& self, Pattern pattern) {
    switch (pattern) {
        case Pattern::OMNIDIRECTIONAL:
            strcpy(self.pattern, "omnidirectional");
            break;
        case Pattern::CARDIOID:
            strcpy(self.pattern, "cardioid");
            break;
        default:
            throw py::value_error("Not supported pattern");
    }
}

std::string mic_to_repr(const mic_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.utils.Mic (";
    ss << "P=(" << self.position.x << "," << self.position.y << "," << self.position.z << "), ";
    ss << "D=(" << self.direction.x << "," << self.direction.y << "," << self.direction.z << "), ";
    ss << self.pattern << ")>";
    return ss.str();
}

void init_mic(py::module &m) {
    py::class_<mic_t> mic(m, "Mic", R"pbdoc(A class representing a microphone.)pbdoc");
    mic.def(py::init(&mic_init), R"pbdoc(Create a new mic containing a position, a direction and a pattern.)pbdoc",
            py::arg("position"), py::arg("direction"), py::arg("pattern"))
        .def_readwrite("position", &mic_t::position, R"pbdoc(Get/set the position of the microphone in meters.)pbdoc")
        .def_readwrite("direction", &mic_t::direction, R"pbdoc(Get/set the direction of the microphone.)pbdoc")
        .def_property("pattern", &mic_get_pattern, &mic_set_pattern, R"pbdoc(Get/set the pattern of the microphone (omnidirectional or cardioid).)pbdoc")
        .def("gain", &mic_gain, R"pbdoc(Return the microphone gain for the given direction.)pbdoc",
            py::arg("direction"))
        .def("__repr__", &mic_to_repr);

    py::enum_<Pattern>(mic, "Pattern")
        .value("OMNIDIRECTIONAL", Pattern::OMNIDIRECTIONAL)
        .value("CARDIOID", Pattern::CARDIOID);
}
