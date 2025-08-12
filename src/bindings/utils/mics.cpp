#include <sstream>

#include <pybind11/stl.h>

#include "mics.h"
#include "error.h"

namespace py = pybind11;

struct mics_deleter {
    void operator()(mics_t* p) const {
        mics_destroy(p);
    }
};

std::shared_ptr<mics_t> mics_init(mics_hardware_t hardware) {
    mics_t* mics = mics_construct(hardware);
    if (mics == nullptr) {
        throw py::value_error(pyodas2_error_message());
    }

    return {mics, mics_deleter()};
}

std::shared_ptr<mics_t> mics_init_uninitialized(size_t num_mics) {
    return {mics_construct_uninitialized(num_mics), mics_deleter()};
}

std::shared_ptr<mics_t> mics_init_list(const std::vector<mic_t>& mics) {
    mics_t* self = mics_construct_uninitialized(mics.size());

    for (size_t i = 0; i < mics.size(); i++) {
        self->mics[i] = mics[i];
    }

    return {self, mics_deleter()};
}

size_t mics_len(const mics_t& self) {
    return self.num_mics;
}

mic_t& mics_get_item(mics_t& self, size_t i) {
    if (i >= self.num_mics) {
        throw py::index_error();
    }
    return self.mics[i];
}

void mics_set_item(mics_t& self, size_t i, const mic_t& value) {
    if (i >= self.num_mics) {
        throw py::index_error();
    }
    self.mics[i] = value;
}

std::string mics_to_repr(const mics_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.utils.Mics (len=" << self.num_mics << ")>";
    return ss.str();
}

void init_mics(pybind11::module& m) {
    py::class_<mics_t, std::shared_ptr<mics_t>> mics(m,
        "Mics",
        R"pbdoc(A class representing a microphone array configuration.)pbdoc");

    py::enum_<mics_hardware_t>(mics, "Hardware", R"pbdoc(An enum for common microphone arrays.)pbdoc")
        .value("RESPEAKER_USB_4", MICS_HARDWARE_RESPEAKER_USB_4)
        .value("RESPEAKER_USB_6", MICS_HARDWARE_RESPEAKER_USB_6)
        .value("MINIDSP_UMA", MICS_HARDWARE_MINIDSP_UMA)
        .value("SC16_DEMO_ARRAY", MICS_HARDWARE_SC16_DEMO_ARRAY)
        .value("SC16F", MICS_HARDWARE_SC16F)
        .value("VIBEUS_CIRCULAR", MICS_HARDWARE_VIBEUS_CIRCULAR)
        .value("SOUNDSKRIT_MUG", MICS_HARDWARE_SOUNDSKRIT_MUG);

    mics.def(py::init(&mics_init),
            R"pbdoc(
            Create the mics for a given microphone array.

            :param hardware: A common microphone array.)pbdoc",
            py::arg("hardware"))
        .def(py::init(&mics_init_uninitialized),
            R"pbdoc(
            Create a uninitialized mics instance.

            :param num_mics: The number of microphones.
            )pbdoc",
            py::arg("num_mics"))
        .def(py::init(&mics_init_list),
            R"pbdoc(
            Create a mics instance for a list.

            :param mics: A list of microphone.)pbdoc",
            py::arg("mics"))
        .def("__len__", &mics_len, R"pbdoc(Get the number of microphones.)pbdoc")
        .def("__getitem__",
            &mics_get_item,
            R"pbdoc(
            Get the mutable microphone at the given index.

            :param index: The index at which to return the microphone.)pbdoc",
            py::arg("index"),
            py::return_value_policy::reference)
        .def("__setitem__",
            &mics_set_item,
            R"pbdoc(
            Set the microphone at the given index.

            :param index: The index at which to assign the microphone.
            :param mic: The microphone to assign at the given index.)pbdoc",
            py::arg("index"),
            py::arg("mic"))
        .def("__repr__", &mics_to_repr);
}

void verify_mics_directions(const mics_t& mics) {
    for (size_t i = 0; i < mics.num_mics; i++) {
        if (fabsf(xyz_l2(mics.mics[i].direction) - 1.f) > 1e-3) {
            throw py::value_error("All microphone direction norms must 1");
        }
    }
}
