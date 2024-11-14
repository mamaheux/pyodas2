#include <sstream>

#include <odas2/signals/dsf.h>

#include "dsf.h"

namespace py = pybind11;

struct dsf_deleter {
    void operator()(dsf_t* p) const {
        dsf_destroy(p);
    }
};

std::shared_ptr<dsf_t> dsf_init(const std::string& label) {
    constexpr size_t MAX_LABEL_SIZE = sizeof(dsf_t::label) - 1;
    if (label.size() > MAX_LABEL_SIZE) {
        throw py::value_error("The label is too long. The maximum length is " + std::to_string(MAX_LABEL_SIZE) + ".");
    }

    return {dsf_construct(label.c_str()), dsf_deleter()};
}

std::string dsf_to_repr(const dsf_t& self) {
    std::stringstream ss;

    ss << "<pyodas2.signals.Dsf>";

    return ss.str();
}

void init_dsf(py::module& m) {
    py::class_<dsf_t, std::shared_ptr<dsf_t>>(m, "Dsf", R"pbdoc(A class representing a dsf signal.)pbdoc")
        .def(py::init(&dsf_init), R"pbdoc(Create a dsf signal.)pbdoc", py::arg("label"))
        .def_readonly("label", &dsf_t::label, R"pbdoc(Get the label.)pbdoc")
        .def_readwrite("sigmoid_mean", &dsf_t::sigmoid_mean, R"pbdoc(Get the sigmoid mean.)pbdoc")
        .def_readwrite("sigmoid_slope", &dsf_t::sigmoid_slope, R"pbdoc(Get the sigmoid slope.)pbdoc")
        .def_readwrite("tracked_source_sigma2", &dsf_t::tracked_source_sigma2, R"pbdoc(Get the tracked source sigma2.)pbdoc")
        .def_readwrite("tracked_source_threshold", &dsf_t::tracked_source_threshold, R"pbdoc(Get the tracked source threshold.)pbdoc")
        .def_readwrite("tracked_source_rate", &dsf_t::tracked_source_rate, R"pbdoc(Get the tracked source rate.)pbdoc")
        .def_readwrite("new_source_sigma2", &dsf_t::new_source_sigma2, R"pbdoc(Get the new source sigma2.)pbdoc")
        .def_readwrite("new_threshold", &dsf_t::new_threshold, R"pbdoc(Get the new threshold.)pbdoc")
        .def_readwrite("delete_threshold", &dsf_t::delete_threshold, R"pbdoc(Get the delete threshold.)pbdoc")
        .def_readwrite("delete_decay", &dsf_t::delete_decay, R"pbdoc(Get the delete decay.)pbdoc")
        .def("__repr__", &dsf_to_repr);
}
