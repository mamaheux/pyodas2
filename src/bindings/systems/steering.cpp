#include <sstream>

#include <odas2/systems/steering.h>

#include "steering.h"
#include "../utils/mics.h"
#include "../signals/doas.h"

namespace py = pybind11;

struct steering_deleter {
    void operator()(steering_t* p) const {
        steering_destroy(p);
    }
};

class Steering {
    std::unique_ptr<steering_t, steering_deleter> m_steering;
    std::shared_ptr<const mics_t> m_mics; // Because steering_t keeps a pointer to it

public:
    Steering(std::shared_ptr<const mics_t> mics, float sample_rate, float sound_speed, size_t num_sources) {
        verify_mics_directions(*mics);
        m_mics = std::move(mics);
        m_steering.reset(steering_construct(m_mics.get(), sample_rate, sound_speed, num_sources));
    }

    [[nodiscard]] size_t num_channels() const {
        return m_steering->num_channels;
    }

    [[nodiscard]] size_t num_pairs() const {
        return m_steering->num_pairs;
    }

    [[nodiscard]] size_t num_sources() const {
        return m_steering->num_sources;
    }

    [[nodiscard]] std::shared_ptr<const mics_t> mics() const {
        return m_mics;
    }

    [[nodiscard]] float sample_rate() const {
        return m_steering->sample_rate;
    }

    [[nodiscard]] float sound_speed() const {
        return m_steering->sound_speed;
    }

    void process(const doas_t& doas, tdoas_t& tdoas) {
        if (m_steering->num_sources != doas.num_directions) {
            throw py::value_error("The number of directions of the doas must be " + std::to_string(m_steering->num_sources) + ".");
        }
        if (m_steering->num_sources != tdoas.num_sources) {
            throw py::value_error("The number of sources of the tdoas must be " + std::to_string(m_steering->num_sources) + ".");
        }
        if (m_steering->num_channels != tdoas.num_channels) {
            throw py::value_error("The number of channels of the tdoas must be " + std::to_string(m_steering->num_channels) + ".");
        }
        verify_doas_direction(doas);

        if (steering_process(m_steering.get(), &doas, &tdoas) != 0) {
            throw std::runtime_error("Failed to process steering");
        }
    }

    std::string to_repr() {
        std::stringstream ss;

        ss << "<pyodas2.systems.Steering (C=" << m_steering->num_channels << ", S=" << m_steering->num_sources << ")>";

        return ss.str();
    }
};

void init_steering(py::module& m) {
    py::class_<Steering, std::shared_ptr<Steering>>(m, "Steering", R"pbdoc(A class representing the steering process.)pbdoc")
        .def(py::init<std::shared_ptr<const mics_t>, float, float, size_t>(), R"pbdoc(Create a steering process.)pbdoc", py::arg("mics"), py::arg("sample_rate"), py::arg("sound_speed"), py::arg("num_sources"))
        .def_property_readonly("num_channels", &Steering::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_property_readonly("num_pairs", &Steering::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_property_readonly("num_sources", &Steering::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_property_readonly("mics", &Steering::mics, R"pbdoc(Get the mics.)pbdoc")
        .def_property_readonly("sample_rate", &Steering::sample_rate, R"pbdoc(Get the sample rate.)pbdoc")
        .def_property_readonly("sound_speed", &Steering::sound_speed, R"pbdoc(Get the sound speed.)pbdoc")
        .def("process", &Steering::process, R"pbdoc(Perform the steering process.)pbdoc", py::arg("doas"), py::arg("tdoas"))
        .def("__repr__", &Steering::to_repr);
}
