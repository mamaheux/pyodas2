#include <sstream>

#include <odas2/utils/mics.h>

#include "mics.h"

namespace py = pybind11;

enum class Hardware {
    RESPEAKER_USB,
    MINIDSP_UMA,
    INTROLAB_CIRCULAR,
    VIBEUS_CIRCULAR,
    SOUNDSKRIT_MUG
};

struct mics_deleter {
    void operator()(mics_t* p) const     {
        mics_destroy(p);
    }
};

std::shared_ptr<mics_t> mics_init(Hardware hardware) {
    switch (hardware) {
        case Hardware::RESPEAKER_USB:
            return {mics_construct("respeaker_usb"), mics_deleter()};
        case Hardware::MINIDSP_UMA:
            return {mics_construct("minidsp_uma"), mics_deleter()};
        case Hardware::INTROLAB_CIRCULAR:
            return {mics_construct("introlab_circular"), mics_deleter()};
        case Hardware::VIBEUS_CIRCULAR:
            return {mics_construct("vibeus_circular"), mics_deleter()};
        case Hardware::SOUNDSKRIT_MUG:
            return {mics_construct("soundskrit_mug"), mics_deleter()};
        default:
            throw py::value_error("Not supported geometry");
    }
}

size_t mics_len(const mics_t& self) {
    return self.num_mics;
}

mic_t& mics_get_item(const mics_t& self, size_t i) {
    if (i >= self.num_mics) {
        throw std::out_of_range("");
    }
    return self.mics[i];
}

void mics_set_item(const mics_t& self, size_t i, const mic_t& value) {
    if (i >= self.num_mics) {
        throw std::out_of_range("");
    }
    self.mics[i] = value;
}

std::string to_repr(const mics_t& self) {
    std::stringstream ss;
    ss << "<pyodas2.utils.Mics (len=" << self.num_mics << ")>";
    return ss.str();
}

std::string to_string(const mics_t& self) {
    std::stringstream ss;
    ss << "Mics = [";
    for (size_t i = 0; i < self.num_mics; i++) {
        ss << "{";
        ss << "P=(" << self.mics[i].position.x << "," << self.mics[i].position.y << "," << self.mics[i].position.z << "), ";
        ss << "D=(" << self.mics[i].direction.x << "," << self.mics[i].direction.y << "," << self.mics[i].direction.z << "), ";
        ss << self.mics[i].pattern << "}";

        if (i < self.num_mics - 1) {
            ss << ",";
        }
    }
    ss << "]";
    return ss.str();
}

void init_mics(pybind11::module& m) {
    py::class_<mics_t, std::shared_ptr<mics_t>> mics(m, "Mics");
    mics.def(py::init(&mics_init), R"pbdoc(Create the mics for a given hardware)pbdoc", py::arg("hardware")) // TODO add a constructor that take a list of Mics
        .def("__len__", &mics_len)
        .def("__getitem__", &mics_get_item, py::return_value_policy::reference)
        .def("__setitem__", &mics_set_item)
        .def("__repr__", &to_repr)
        .def("__str__", &to_string);

    py::enum_<Hardware>(mics, "Hardware")
        .value("RESPEAKER_USB", Hardware::RESPEAKER_USB)
        .value("MINIDSP_UMA", Hardware::MINIDSP_UMA)
        .value("INTROLAB_CIRCULAR", Hardware::INTROLAB_CIRCULAR)
        .value("VIBEUS_CIRCULAR", Hardware::VIBEUS_CIRCULAR)
        .value("SOUNDSKRIT_MUG", Hardware::SOUNDSKRIT_MUG);
}
