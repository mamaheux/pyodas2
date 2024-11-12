#include <sstream>

#include <odas2/systems/stft.h>

#include "stft.h"

namespace py = pybind11;

enum class Window {
    HANN,
    SINE
};

struct stft_deleter {
    void operator()(stft_t* p) const {
        stft_destroy(p);
    }
};

std::shared_ptr<stft_t> stft_init(size_t num_channels, size_t num_samples, size_t num_shifts, Window window) {
    if (ceilf(log2f(static_cast<float>(num_samples))) != floorf(log2f(static_cast<float>(num_samples)))) {
        throw py::value_error("The number of samples must be a power of 2 and the number of bins must be (num_samples / 2) + 1.");
    }
    if (num_shifts > num_samples) {
        throw py::value_error("The number of samples must be higher than number of shifts.");
    }
    size_t num_bins = (num_samples / 2) + 1;

    switch (window) {
        case Window::HANN:
            return {stft_construct(num_channels, num_samples, num_shifts, num_bins, "hann"), stft_deleter()};
        case Window::SINE:
            return {stft_construct(num_channels, num_samples, num_shifts, num_bins, "sine"), stft_deleter()};
        default:
            throw py::value_error("Not supported window");
    }
}

void stft_process_python(stft_t& self, const hops_t& hops, freqs_t& freqs) {
    if (self.num_channels != hops.num_channels) {
        throw py::value_error("The number of sources of the hops must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != freqs.num_channels) {
        throw py::value_error("The number of channels of the freqs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_shifts != hops.num_shifts) {
        throw py::value_error("The number of shifts of the hops must be " + std::to_string(self.num_shifts) + ".");
    }
    if (self.num_bins != freqs.num_bins) {
        throw py::value_error("The number of bins of the freqs must be " + std::to_string(self.num_bins) + ".");
    }

    if (stft_process(&self, &hops, &freqs) != 0) {
        throw std::runtime_error("Failed to process gcc");
    }
}

std::string stft_to_repr(const stft_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Stft (C=" << self.num_channels << ", Sa=" << self.num_samples;
    ss << ", Sh=" << self.num_shifts << ", B=" << self.num_bins << ")>";

    return ss.str();
}

struct istft_deleter {
    void operator()(istft_t* p) const {
        istft_destroy(p);
    }
};

std::shared_ptr<istft_t> istft_init(size_t num_channels, size_t num_samples, size_t num_shifts, Window window) {
    if (ceilf(log2f(static_cast<float>(num_samples))) != floorf(log2f(static_cast<float>(num_samples)))) {
        throw py::value_error("The number of samples must be a power of 2 and the number of bins must be (num_samples / 2) + 1.");
    }
    if (num_shifts > num_samples) {
        throw py::value_error("The number of samples must be higher than number of shifts.");
    }
    size_t num_bins = (num_samples / 2) + 1;

    switch (window) {
        case Window::HANN:
            return {istft_construct(num_channels, num_samples, num_shifts, num_bins, "hann"), istft_deleter()};
        case Window::SINE:
            return {istft_construct(num_channels, num_samples, num_shifts, num_bins, "sine"), istft_deleter()};
        default:
            throw py::value_error("Not supported window");
    }
}

void istft_process_python(istft_t& self, const freqs_t& freqs, hops_t& hops) {
    if (self.num_channels != hops.num_channels) {
        throw py::value_error("The number of sources of the hops must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_channels != freqs.num_channels) {
        throw py::value_error("The number of channels of the freqs must be " + std::to_string(self.num_channels) + ".");
    }
    if (self.num_shifts != hops.num_shifts) {
        throw py::value_error("The number of shifts of the hops must be " + std::to_string(self.num_shifts) + ".");
    }
    if (self.num_bins != freqs.num_bins) {
        throw py::value_error("The number of bins of the freqs must be " + std::to_string(self.num_bins) + ".");
    }

    if (istft_process(&self, &freqs, &hops) != 0) {
        throw std::runtime_error("Failed to process gcc");
    }
}

std::string istft_to_repr(const stft_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Istft (C=" << self.num_channels << ", Sa=" << self.num_samples;
    ss << ", Sh=" << self.num_shifts << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_stft_istft(pybind11::module& m) {
    py::enum_<Window>(m, "Window")
        .value("HANN", Window::HANN)
        .value("SINE", Window::SINE);

    py::class_<stft_t, std::shared_ptr<stft_t>>(m, "Stft", R"pbdoc(A class representing the stft process.)pbdoc")
        .def(py::init(&stft_init), R"pbdoc(Create a stft process.)pbdoc", py::arg("num_channels"), py::arg("num_samples"), py::arg("num_shifts"), py::arg("window"))
        .def_readonly("num_channels", &stft_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_samples", &stft_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("num_shifts", &stft_t::num_shifts, R"pbdoc(Get the number of shifts.)pbdoc")
        .def_readonly("num_bins", &stft_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &stft_process_python, R"pbdoc(Perform the stft process.)pbdoc", py::arg("hops"), py::arg("freqs"))
    .def("__repr__", &stft_to_repr);

    py::class_<istft_t, std::shared_ptr<istft_t>>(m, "Istft", R"pbdoc(A class representing the istft process.)pbdoc")
        .def(py::init(&istft_init), R"pbdoc(Create a istft process.)pbdoc", py::arg("num_channels"), py::arg("num_samples"), py::arg("num_shifts"), py::arg("window"))
        .def_readonly("num_channels", &istft_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_samples", &istft_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("num_shifts", &istft_t::num_shifts, R"pbdoc(Get the number of shifts.)pbdoc")
        .def_readonly("num_bins", &istft_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process", &istft_process_python, R"pbdoc(Perform the istft process.)pbdoc", py::arg("freqs"), py::arg("hops"))
        .def("__repr__", &istft_to_repr);
}
