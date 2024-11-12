#ifndef __BINDINGS__MICS_H
#define __BINDINGS__MICS_H

#include <pybind11/pybind11.h>

#include <odas2/utils/mics.h>

void init_mics(pybind11::module& m);

void verify_mics_directions(const mics_t& mics);

#endif // __BINDINGS__MIC_H
