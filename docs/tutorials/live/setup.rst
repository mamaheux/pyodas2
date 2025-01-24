1. Setup
#########

Below are the instructions to config your computer for live processing depending of your computer.
Some tutorials use the visualization classes, so PyODAS2 must be installed with the visualization optional dependencies.
They contain PySide6 which has a LGPL licence.

64-bitsRaspberry Pi Computers
******************************

.. code-block:: bash

    sudo apt install libcap-dev python3-libcamera python3-picamera2
    python3 -m venv --system-site-packages venv
    source venv/bin/activate
    pip install pyodas2[visualization] pyalsaaudio

Other Computers:
*****************

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    pip install pyodas2[visualization] pyalsaaudio
