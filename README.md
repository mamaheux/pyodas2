# PyODAS2: Python Open embedded Audition System 2

![example workflow](https://github.com/mamaheux/pyodas2/actions/workflows/release.yml/badge.svg)

**PyODAS2** is an advanced Python library designed for embedded audio processing applications. Its primary focus is to 
enable developers and researchers to achieve sound source localization, tracking, separation, and acoustic imaging  with
ease and efficiency. The library is built with simplicity, flexibility, and scalability in mind, making it a versatile 
tool for a wide range of real-world audio processing tasks.

---

## Overview

Modern systems in robotics, surveillance, and audio applications increasingly rely on sound for interaction and
functionality. PyODAS2 bridges the gap between theoretical sound processing techniques and practical implementation, 
offering a ready-to-use, open-source framework for audio-based systems.

By using PyODAS2, you can:
- Pinpoint the location of sound sources in 3D space.
- Dynamically track moving audio sources over time.
- Separate individual audio signals from a mix for clarity and analysis.
- Visualize sound fields with acoustic images.

PyODAS2 is designed to work seamlessly on embedded systems, ensuring low latency and high performance even in
constrained environments.

---

## Key Features

### 1. **Sound Source Localization**
PyODAS2 uses advanced algorithms to detect and determine the spatial position of sound sources. Whether you’re working
on a robot navigating through noisy environments or designing a surveillance system, this feature is critical.

### 2. **Sound Source Tracking**
The library supports real-time tracking of moving sound sources. It ensures robust and continuous monitoring, even in 
dynamic environments.

### 3. **Sound Separation**
PyODAS2 includes tools to isolate individual sound sources from complex audio mixtures, enabling clean signal extraction
and detailed analysis.

### 4. **Acoustic Imaging**
Generate visual representations of sound fields, providing insights into sound distribution and directionality within an
environment.

### 5. **Embeddability**
Built with embedded systems in mind, PyODAS2 is lightweight and efficient, making it suitable for resource-constrained 
hardware setups.

---

## Getting Started
To start using PyODAS2, you can execute the following command to install PyODAS2:
```bash
pip install pyodas2
```

For examples, check out the [examples](examples) directory in the repository.

## Documentation

Comprehensive documentation is available to guide you through the features and functionalities of PyODAS2. Visit the 
[documentation page](https://mamaheux.github.io/pyodas2/) for detailed guides, API references, and tutorials.

## Contributing

We welcome contributions to PyODAS2! If you'd like to contribute, follow these steps:

1. Fork the repository.
2. Clone your fork.
3. Install PyODAS2 in editable mode
```bash
pip install .[dev]
```

4. Create a new branch for your feature or bug fix:
```bash
git checkout -b feature-name
```

5. Make your changes and commit them:
```bash
git commit -m "Add new feature or fix"
```

6. Push your changes to your fork:
```bash
git push origin feature-name
```

7. Make sure all tests pass:
```bash
pytest
```

8. Make sure there is no linter warnings:
```bash
ruff check
```

9. Submit a pull request, and we’ll review it as soon as possible.

---

## Licence 
This project is licensed under the MIT License. You’re free to use, modify, and distribute PyODAS2 in your projects with
attribution.
