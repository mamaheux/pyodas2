pyodas2.visualization
######################

To use the following classes, PyODAS2 must be installed with the visualization optional dependencies. They contain
PySide6 which has a LGPL licence.

.. code-block:: bash

    pip install pyodas2[visualization]


Classes
********

.. autoclass:: pyodas2.visualization.AcousticImageCalibrationWidget

   .. automethod:: __init__
   .. automethod:: set_camera_image
   .. automethod:: set_targets

.. autoclass:: pyodas2.visualization.AcousticImageWidget

   .. automethod:: __init__
   .. automethod:: set_images

.. autoclass:: pyodas2.visualization.SourceLocationWidget

   .. automethod:: __init__
   .. automethod:: set_potential_sources
   .. automethod:: set_tracked_sources

.. autoclass:: pyodas2.visualization.ElevationAzimuthWidget

   .. automethod:: __init__
   .. automethod:: add_potential_sources
   .. automethod:: add_tracked_sources
