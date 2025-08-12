#include <sstream>

#include <odas2/utils/mics.h>

#include "mic.h"

namespace py = pybind11;

mic_t mic_init(const xyz_t position, const xyz_t direction, mic_pattern_t pattern) {
    return mic_cst(position, xyz_unit(direction), pattern);
}

const char* pattern_to_string(mic_pattern_t pattern) {
    switch (pattern) {
        case MIC_PATTERN_OMNIDIRECTIONAL:
            return "omnidirectional";
        case MIC_PATTERN_CARDIOID:
            return "cardioid";
        default:
            return "unknown";
    }
}

std::string mic_to_repr(const mic_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.utils.Mic (";
    ss << "P=(" << self.position.x << "," << self.position.y << "," << self.position.z << "), ";
    ss << "D=(" << self.direction.x << "," << self.direction.y << "," << self.direction.z << "), ";
    ss << pattern_to_string(self.pattern) << ")>";
    return ss.str();
}

void init_mic(py::module &m) {
    py::class_<mic_t> mic(m, "Mic", R"pbdoc(A class representing a microphone.)pbdoc");

    py::enum_<mic_pattern_t>(mic, "Pattern", R"pbdoc(An enum representing microphone patterns.)pbdoc")
        .value("OMNIDIRECTIONAL", MIC_PATTERN_OMNIDIRECTIONAL)
        .value("CARDIOID", MIC_PATTERN_CARDIOID);

    mic.def(py::init(&mic_init),
            R"pbdoc(
            Create a new mic containing a position, a direction and a pattern.

            :param position: The microphone position in meters.
            :param position: The microphone direction.
            :param pattern: The microphone pattern.)pbdoc",
            py::arg("position"),
            py::arg("direction"),
            py::arg("pattern"))
        .def_readwrite("position", &mic_t::position, R"pbdoc(Get/set the position of the microphone in meters.)pbdoc")
        .def_readwrite("direction", &mic_t::direction, R"pbdoc(Get/set the direction of the microphone.)pbdoc")
        .def_readwrite("pattern",
            &mic_t::pattern,
            R"pbdoc(Get/set the pattern of the microphone (omnidirectional or cardioid).)pbdoc")
        .def("gain",
            &mic_gain,
            R"pbdoc(
            Return the microphone gain for the given direction.

            :param direction: The direction in which to get the gain.)pbdoc",
            py::arg("direction"))
        .def("__repr__", &mic_to_repr);
}
