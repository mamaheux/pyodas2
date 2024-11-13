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
        src/bindings/main.cpp

        src/bindings/signals/covs.cpp
        src/bindings/signals/doas.cpp
        src/bindings/signals/freqs.cpp
        src/bindings/signals/hops.cpp
        src/bindings/signals/masks.cpp
        src/bindings/signals/tdoas.cpp
        src/bindings/signals/weights.cpp

        src/bindings/systems/beamformer.cpp
        src/bindings/systems/delaysum.cpp
        src/bindings/systems/gcc.cpp
        src/bindings/systems/mixer.cpp
        src/bindings/systems/mvdr.cpp
        src/bindings/systems/phat.cpp
        src/bindings/systems/scm.cpp
        src/bindings/systems/ssl.cpp
        src/bindings/systems/sst.cpp
        src/bindings/systems/steering.cpp
        src/bindings/systems/stft.cpp

        src/bindings/types/xyz.cpp

        src/bindings/utils/mic.cpp
        src/bindings/utils/mics.cpp
        src/bindings/utils/points.cpp
        WITH_SOABI)
target_include_directories(_core PUBLIC src/odas2/core/include)
target_link_libraries(_core PUBLIC pybind11::module odas2)

# This is passing in the version as a define just as an example
target_compile_definitions(_core PRIVATE VERSION_INFO=${PROJECT_VERSION})

# The install directory is the output (wheel) directory
install(TARGETS _core DESTINATION pyodas2)
