4. Sound Source Separation (SSS) Using the Delay-and-Sum Beamformer
####################################################################

This tutorial demonstrates how to perform sound source separation (SSS) using the delay-and-sum beamformer to amplify
the dominant sound captured by the microphone array. If there are many dominant sounds, it is likely that the beamformer
alternates between the sounds. Next tutorials will cover more robust applications of the delay-and-sum beamformer.

The delay-and-sum beamformer works by taking signals from multiple microphones (or sensors) and applying time delays to
each microphone’s signal to align them in such a way that sound from a specific direction is reinforced, while sounds
from other directions are minimized. This process effectively "focuses" the microphone array on a particular sound
source, improving the signal-to-noise ratio for sounds from that direction and reducing interference from others.
It’s commonly used in applications like speech recognition, conference systems, and directional hearing aids. Here's how
it works in PyODAS2:

1. **Determine TDOAs (Time Differences of Arrival) between microphone pairs.** TDOA represents the time delay between
   the arrival of a sound at two microphones. As sound travels at a constant speed (e.g., the speed of sound in air),
   microphones placed at different positions will detect the sound at slightly different times. By examining these time
   delays between microphone pairs, the system can estimate the origin of the sound. This process involves accurately
   calculating these delays using methods like cross-correlation, which identifies the time shift where the signals from
   the two microphones are most closely aligned.

2. **Apply the delay-and-sum beamformer.** The audio signals received by each microphone in the array are delayed by a
   calculated amount calculated in step 1. After the delaying them, the signals are summed together, creating a composite
   signal that emphasizes the dominant sound.

Below is a breakdown of the code.

A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import os
    import wave

    from pyodas2.pcm import interleaved_pcm_to_numpy, numpy_to_interleaved_pcm
    from pyodas2.pipelines import DelaySumPipeline
    from pyodas2.utils import Mics

Below is a description of the imports:

* :code:`os`, :code:`wave`: Standard libraries for handling file paths and WAV audio files.

* :code:`pyodas2.pcm.interleaved_pcm_to_numpy`: Converts interleaved PCM audio data into a NumPy array for processing.

* :code:`pyodas2.pcm.numpy_to_interleaved_pcm`: Converts a NumPy array into interleaved PCM audio data.

* :code:`pyodas2.pipelines.DelaySumPipeline`: The delay-and-sound pipeline performs sound source separation of the
  dominant sound.

* :code:`pyodas2.utils.Mics`: Provides microphone configurations, in this case, for the SC-16F microphone array.

TODO

Summary
********

.. include:: ../../../examples/file/delay_sum_example.py
   :literal:
