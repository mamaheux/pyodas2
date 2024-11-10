# Require CMake 3.15+ (matching scikit-build-core) Use new versions of all
# policies up to CMake 3.27
cmake_minimum_required(VERSION 3.15...3.27)

set(BUILD_SHARED_LIBS OFF)
add_subdirectory(src/odas2/core)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Add a library using FindPython's tooling (pybind11 also provides a helper like
# this)
python_add_library(_core MODULE
        src/binding/main.cpp
        src/binding/signals/freqs.cpp
        src/binding/signals/hops.cpp
        src/binding/types/xyz.cpp
        src/binding/utils/mic.cpp
        src/binding/utils/mics.cpp
        src/binding/utils/points.cpp
        WITH_SOABI)
target_include_directories(_core PUBLIC src/odas2/core/include)
target_link_libraries(_core PUBLIC pybind11::module odas2)

# This is passing in the version as a define just as an example
target_compile_definitions(_core PRIVATE VERSION_INFO=${PROJECT_VERSION})

# The install directory is the output (wheel) directory
install(TARGETS _core DESTINATION pyodas2)
