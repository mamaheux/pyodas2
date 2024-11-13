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

|

.. autoclass:: pyodas2.systems.Phat

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.systems.Scm

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_bins
   .. autoproperty:: alpha

|

.. autoclass:: pyodas2.systems.Ssl

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_sources
   .. autoproperty:: num_directions
   .. autoproperty:: num_points
   .. autoproperty:: sample_rate
   .. autoproperty:: sound_speed
   .. autoproperty:: mics
   .. autoproperty:: points

|

.. autoclass:: pyodas2.systems.Sst

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_tracks
   .. autoproperty:: num_directions
   .. autoproperty:: delta_time
   .. autoproperty:: energy_threshold

|

.. autoclass:: pyodas2.systems.Window
   :members:
   :exclude-members: name

|

.. autoclass:: pyodas2.systems.Steering

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_sources
   .. autoproperty:: mics
   .. autoproperty:: sample_rate
   .. autoproperty:: sound_speed

|

.. autoclass:: pyodas2.systems.Stft

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_samples
   .. autoproperty:: num_shifts
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.systems.Istft

   .. automethod:: __init__

   .. automethod:: process

   .. autoproperty:: num_channels
   .. autoproperty:: num_samples
   .. autoproperty:: num_shifts
   .. autoproperty:: num_bins

|
