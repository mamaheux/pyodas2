pyodas2.signals
===============

Classes
----------------
.. autoclass:: pyodas2.signals.Covs

   .. automethod:: __init__

   .. automethod:: xcorrs_load_numpy
   .. automethod:: xcorrs_to_numpy
   .. automethod:: acorrs_load_numpy
   .. automethod:: acorrs_to_numpy

   .. autoproperty:: label
   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.signals.Doas

   .. automethod:: __init__

   .. automethod:: __len__
   .. automethod:: __getitem__
   .. automethod:: __setitem__

   .. autoproperty:: label

.. autoclass:: pyodas2.signals::Doas.Src
   :members:
   :exclude-members: name

.. autoclass:: pyodas2.signals::Doas.Dir
   :special-members: __init__
   :members:

|

.. autoclass:: pyodas2.signals.Dsf

   .. automethod:: __init__

   .. autoproperty:: label
   .. autoproperty:: sigmoid_mean
   .. autoproperty:: sigmoid_slope
   .. autoproperty:: tracked_source_sigma2
   .. autoproperty:: tracked_source_threshold
   .. autoproperty:: tracked_source_rate
   .. autoproperty:: new_source_sigma2
   .. autoproperty:: new_threshold
   .. autoproperty:: delete_threshold
   .. autoproperty:: delete_decay

|

.. autoclass:: pyodas2.signals.Freqs

   .. automethod:: __init__

   .. automethod:: load_numpy
   .. automethod:: to_numpy

   .. autoproperty:: label
   .. autoproperty:: num_channels
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.signals.Hops

   .. automethod:: __init__

   .. automethod:: load_numpy
   .. automethod:: to_numpy

   .. autoproperty:: label
   .. autoproperty:: num_channels
   .. autoproperty:: num_shifts
   .. autoproperty:: num_samples

|

.. autoclass:: pyodas2.signals.Masks

   .. automethod:: __init__

   .. automethod:: load_numpy
   .. automethod:: to_numpy

   .. autoproperty:: label
   .. autoproperty:: num_channels
   .. autoproperty:: num_bins

|

.. autoclass:: pyodas2.signals.Tdoas

   .. automethod:: __init__

   .. automethod:: __getitem__
   .. automethod:: __setitem__

   .. autoproperty:: label
   .. autoproperty:: shape
   .. autoproperty:: num_sources
   .. autoproperty:: num_channels
   .. autoproperty:: num_pairs

.. autoclass:: pyodas2.signals::Tdoas.Tau
   :special-members: __init__
   :members:

|

.. autoclass:: pyodas2.signals.Weights

   .. automethod:: __init__

   .. automethod:: load_numpy
   .. automethod:: to_numpy

   .. autoproperty:: label
   .. autoproperty:: num_sources
   .. autoproperty:: num_channels
   .. autoproperty:: num_bins
