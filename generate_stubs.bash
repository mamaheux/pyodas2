#!/bin/bash

export PYTHONPATH="$PYTHONPATH:$PWD"
pybind11-stubgen pyodas2 -o $PWD
