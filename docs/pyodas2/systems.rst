pyodas2.systems
===============

Classes
----------------
.. autoclass:: pyodas2.systems.Beamformer

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_sources
   .. autoproperty:: num_channels
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.systems.DelaySum

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_sources
   .. autoproperty:: num_channels
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.systems.Gcc

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_sources
   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_bins
   .. autoproperty:: num_samples
   .. autoproperty:: interpolation_factor

|

.. autoclass:: pyodas2.systems.Mixer

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels

|

.. autoclass:: pyodas2.systems.Mvdr

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_bins
