#include <sstream>

#include <odas2/systems/ssl.h>

#include "ssl.h"
#include "../utils/mics.h"

namespace py = pybind11;

struct ssl_deleter {
    void operator()(ssl_t* p) const {
        ssl_destroy(p);
    }
};

class Ssl {
    std::unique_ptr<ssl_t, ssl_deleter> m_ssl;
    std::shared_ptr<const mics_t> m_mics; // Because ssl_t keeps a pointer to it
    std::shared_ptr<const points_t> m_points; // Because ssl_t keeps a pointer to it

public:
    Ssl(std::shared_ptr<const mics_t> mics, std::shared_ptr<const points_t> points, float sample_rate, float sound_speed, size_t num_sources, size_t num_directions) {
        verify_mics_directions(*mics);
        m_mics = std::move(mics);
        m_points = std::move(points);
        m_ssl.reset(ssl_construct(m_mics.get(), m_points.get(), sample_rate, sound_speed, num_sources, num_directions));
    }

    [[nodiscard]] size_t num_channels() const {
        return m_ssl->num_channels;
    }

    [[nodiscard]] size_t num_pairs() const {
        return m_ssl->num_pairs;
    }

    [[nodiscard]] size_t num_sources() const {
        return m_ssl->num_sources;
    }

    [[nodiscard]] size_t num_directions() const {
        return m_ssl->num_directions;
    }

    [[nodiscard]] size_t num_points() const {
        return m_ssl->num_points;
    }

    [[nodiscard]] float sample_rate() const {
        return m_ssl->sample_rate;
    }

    [[nodiscard]] float sound_speed() const {
        return m_ssl->sound_speed;
    }

    [[nodiscard]] std::shared_ptr<const mics_t> mics() const {
        return m_mics;
    }

    [[nodiscard]] std::shared_ptr<const points_t> points() const {
        return m_points;
    }

    void process(const tdoas_t& tdoas, doas_t& doas) {
        if (m_ssl->num_sources != tdoas.num_sources) {
            throw py::value_error("The number of sources of the tdoas must be " + std::to_string(m_ssl->num_sources) + ".");
        }
        if (m_ssl->num_channels != tdoas.num_channels) {
            throw py::value_error("The number of channels of the tdoas must be " + std::to_string(m_ssl->num_channels) + ".");
        }
        if (m_ssl->num_directions != doas.num_directions) {
            throw py::value_error("The number of directions of the doas must be " + std::to_string(m_ssl->num_directions) + ".");
        }

        if (ssl_process(m_ssl.get(), &tdoas, &doas) != 0) {
            throw std::runtime_error("Failed to process ssl");
        }
    }

    std::string to_repr() {
        std::stringstream ss;

        ss << "<pyodas2.systems.Ssl (S=" << m_ssl->num_sources << ", D=" << m_ssl->num_directions << ")>";

        return ss.str();
    }
};

void init_ssl(py::module& m) {
    py::class_<Ssl, std::shared_ptr<Ssl>>(m, "Ssl", R"pbdoc(A class representing the ssl process.)pbdoc")
        .def(py::init<std::shared_ptr<const mics_t>, std::shared_ptr<const points_t>, float, float, size_t, size_t>(),
            R"pbdoc(Create a ssl process.)pbdoc",
            py::arg("mics"), py::arg("points"), py::arg("sample_rate"), py::arg("sound_speed"), py::arg("num_sources"), py::arg("num_directions"))
        .def_property_readonly("num_channels", &Ssl::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_property_readonly("num_pairs", &Ssl::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def_property_readonly("num_sources", &Ssl::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_property_readonly("num_directions", &Ssl::num_directions, R"pbdoc(Get the number of directions.)pbdoc")
        .def_property_readonly("num_points", &Ssl::num_points, R"pbdoc(Get the number of points.)pbdoc")
        .def_property_readonly("sample_rate", &Ssl::sample_rate, R"pbdoc(Get the sample rate.)pbdoc")
        .def_property_readonly("sound_speed", &Ssl::sound_speed, R"pbdoc(Get the sound speed.)pbdoc")
        .def_property_readonly("mics", &Ssl::mics, R"pbdoc(Get the mics.)pbdoc")
        .def_property_readonly("points", &Ssl::points, R"pbdoc(Get the points.)pbdoc")
        .def("process", &Ssl::process, R"pbdoc(Perform the ssl process.)pbdoc", py::arg("tdoas"), py::arg("doas"))
        .def("__repr__", &Ssl::to_repr);
}
