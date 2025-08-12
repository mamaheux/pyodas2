#!/bin/bash

echo "Generating stubs for pyodas2..."

export PYTHONPATH="$PYTHONPATH:$PWD"
pybind11-stubgen pyodas2 -o $PWD
