#ifndef __BINDINGS__DOAS_H
#define __BINDINGS__DOAS_H

#include <pybind11/pybind11.h>

#include <odas2/signals/doas.h>

void init_doas(pybind11::module& m);

void verify_doas_direction(const doas_t& doas);

#endif // __BINDINGS__DOAS_H
