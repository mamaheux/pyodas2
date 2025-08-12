#include <sstream>

#include <odas2/systems/stft.h>

#include "stft.h"
#include "../utils/error.h"

namespace py = pybind11;

struct stft_deleter {
    void operator()(stft_t* p) const {
        stft_destroy(p);
    }
};

std::shared_ptr<stft_t> stft_init(size_t num_channels, size_t num_samples, size_t num_shifts, stft_window_t window) {
    stft_t* stft = stft_construct(num_channels, num_samples, num_shifts, window);
    if (stft == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {stft, stft_deleter()};
}

void stft_process_python(stft_t& self, const hops_t& hops, freqs_t& freqs) {
    if (stft_process(&self, &hops, &freqs) != 0) {
        throw py::value_error(pyodas2_error_message());
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

std::shared_ptr<istft_t> istft_init(size_t num_channels, size_t num_samples, size_t num_shifts, stft_window_t window) {
    istft_t* istft = istft_construct(num_channels, num_samples, num_shifts, window);
    if (istft == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {istft, istft_deleter()};
}

void istft_process_python(istft_t& self, const freqs_t& freqs, hops_t& hops) {
    if (istft_process(&self, &freqs, &hops) != 0) {
        throw py::value_error(pyodas2_error_message());
    }
}

std::string istft_to_repr(const istft_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.systems.Istft (C=" << self.num_channels << ", Sa=" << self.num_samples;
    ss << ", Sh=" << self.num_shifts << ", B=" << self.num_bins << ")>";

    return ss.str();
}

void init_stft_istft(pybind11::module& m) {
    py::enum_<stft_window_t>(m,
            "Window",
            R"pbdoc(An enum representing windows to compute the Short-time Fourier transform.)pbdoc")
        .value("HANN", STFT_WINDOW_HANN)
        .value("SINE", STFT_WINDOW_SINE);

    py::class_<stft_t, std::shared_ptr<stft_t>>(m,
            "Stft",
            R"pbdoc(A class representing the Short-time Fourier transform (STFT) process.)pbdoc")
        .def(py::init(&stft_init),
            R"pbdoc(
            Create a Stft instance.

            :param num_channels: The number of channels.
            :param num_samples: The number of samples in the FFT which must be a power of 2.
            :param num_shifts: The shift size in samples to compute the STFT which must be at most to num_samples / 2 for perfect reconstruction.
            :param window: The window to compute the FFT.)pbdoc",
            py::arg("num_channels"),
            py::arg("num_samples"),
            py::arg("num_shifts"),
            py::arg("window"))
        .def_readonly("num_channels", &stft_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_samples", &stft_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("num_shifts", &stft_t::num_shifts, R"pbdoc(Get the number of shifts.)pbdoc")
        .def_readonly("num_bins", &stft_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process",
            &stft_process_python,
            R"pbdoc(
            Perform the Short-time Fourier transform. The argument parameters must match those of the instance.

            :param hops: The next audio sample in the time domain to process.
            :param freqs: The result of the Short-time Fourier transform in the frequency domain.
            )pbdoc",
            py::arg("hops"),
            py::arg("freqs"))
    .def("__repr__", &stft_to_repr);

    py::class_<istft_t, std::shared_ptr<istft_t>>(m,
            "Istft",
            R"pbdoc(A class representing the inverse Short-time Fourier transform (ISTFT) process.)pbdoc")
        .def(py::init(&istft_init),
            R"pbdoc(
            Create a inverse Short-time Fourier transform (ISTFT) process.

            :param num_channels: The number of channels.
            :param num_samples: The number of samples in the IFFT which must be a power of 2.
            :param num_shifts: The shift size in samples to compute the ISTFT which must be at most to num_samples / 2 for perfect recoonstruction.
            :param window: The window to compute the IFFT.)pbdoc",
            py::arg("num_channels"),
            py::arg("num_samples"),
            py::arg("num_shifts"),
            py::arg("window"))
        .def_readonly("num_channels", &istft_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_samples", &istft_t::num_samples, R"pbdoc(Get the number of samples.)pbdoc")
        .def_readonly("num_shifts", &istft_t::num_shifts, R"pbdoc(Get the number of shifts.)pbdoc")
        .def_readonly("num_bins", &istft_t::num_bins, R"pbdoc(Get the number of bins.)pbdoc")
        .def("process",
            &istft_process_python,
            R"pbdoc(
            Perform the inverse Short-time Fourier transform.

            :param freqs: The input of the inverse Short-time Fourier transform in the frequency domain.
            :param hops: The result of the inverse Short-time Fourier transform in the time domain.)pbdoc",
            py::arg("freqs"),
            py::arg("hops"))
        .def("__repr__", &istft_to_repr);
}
