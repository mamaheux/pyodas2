#include <tuple>
#include <sstream>

#include <pybind11/stl.h>

#include <odas2/signals/tdoas.h>

#include "tdoas.h"

namespace py = pybind11;

struct tdoas_deleter {
    void operator()(tdoas_t* p) const {
        tdoas_destroy(p);
    }
};

std::shared_ptr<tdoas_t> tdoas_init(const std::string& label, size_t num_channels, size_t num_sources) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(tdoas_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {tdoas_construct(label.c_str(), num_channels, num_sources), tdoas_deleter()};
}

std::tuple<size_t, size_t> tdoas_shape(const tdoas_t& self) {
    return {self.num_sources, self.num_pairs};
}

tau_t& tdoas_get_item(tdoas_t& self, const std::tuple<size_t, size_t>& indexes) {
    if (std::get<0>(indexes) >= self.num_sources || std::get<1>(indexes) >= self.num_pairs) {
        throw py::index_error();
    }
    return self.taus[std::get<0>(indexes)][std::get<1>(indexes)];
}

void tdoas_set_item(tdoas_t& self, const std::tuple<size_t, size_t>& indexes, tau_t tau) {
    if (std::get<0>(indexes) >= self.num_sources || std::get<1>(indexes) >= self.num_pairs) {
        throw py::index_error();
    }
    self.taus[std::get<0>(indexes)][std::get<1>(indexes)] = tau;
}

std::string tdoas_repr(const tdoas_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Tdoas (" << self.label;
    ss << ", C=" << self.num_channels << ", S=" << self.num_sources << ", P=" << self.num_pairs << ")>";

    return ss.str();
}

tau_t tau_init(float delay, float amplitude) {
    return {delay, amplitude};
}

std::string tau_repr(const tau_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Tdoas.Tau (D=" << self.delay << ", A=" << self.amplitude << ")>";

    return ss.str();
}

void init_tdoas(pybind11::module& m) {
    py::class_<tdoas_t, std::shared_ptr<tdoas_t>> tdoas(m, "Tdoas", R"pbdoc(A class representing time differences of arrival.)pbdoc");

    py::class_<tau_t>(tdoas, "Tau", R"pbdoc(A class representing a time difference of arrival.)pbdoc")
        .def(py::init(&tau_init), R"pbdoc(Create a direction of arrival.)pbdoc", py::arg("delay"), py::arg("amplitude"))
        .def_readwrite("delay", &tau_t::delay, R"pbdoc(Get/set the delay.)pbdoc")
        .def_readwrite("amplitude", &tau_t::amplitude, R"pbdoc(Get/set the amplitude.)pbdoc")
        .def("__repr__", &tau_repr);

    tdoas.def(py::init(&tdoas_init), R"pbdoc(Create tdoas.)pbdoc", py::arg("label"), py::arg("num_channels"), py::arg("num_sources"))
        .def_readonly("label", &tdoas_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_property_readonly("shape", &tdoas_shape, R"pbdoc(Get the shape.)pbdoc")
        .def_readonly("num_sources", &tdoas_t::num_sources, R"pbdoc(Get the number of sources.)pbdoc")
        .def_readonly("num_channels", &tdoas_t::num_channels, R"pbdoc(Get the number of channels.)pbdoc")
        .def_readonly("num_pairs", &tdoas_t::num_pairs, R"pbdoc(Get the number of pairs.)pbdoc")
        .def("__getitem__", &tdoas_get_item, R"pbdoc(Get the mutable time difference of arrival at the given indexes (source_index, pair_index).)pbdoc", py::arg("indexes"), py::return_value_policy::reference)
        .def("__setitem__", &tdoas_set_item, R"pbdoc(Set the time differences of arrival at the given indexes (source_index, pair_index).)pbdoc", py::arg("indexes"), py::arg("tau"))
        .def("__repr__", &tdoas_repr);
}
