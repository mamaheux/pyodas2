6. Sound Source Separation (SSS) Using the Delay and Sum Beamformer and Tracked Sources
########################################################################################

This tutorial assumes that you have already gone through this :doc:`one <../file/sst_delay_sum>`. This tutorial
demonstrates how to perform real-time sound source separation by outputting the most dominant tracked sound to the
default audio output. Headphones are required to avoid feedback.

Below is a breakdown of the code.

A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import alsaaudio
    import numpy as np

    from pyodas2.pcm import interleaved_pcm_to_numpy, numpy_to_interleaved_pcm
    from pyodas2.pipelines import SstDelaySumPipeline, SstDelaySumPipelineResult
    from pyodas2.utils import Mics

Compared to the pre-recorded tutorial, the following imports are also required:

* :code:`alsaaudio`: Handles sound cards on Linux.

* :code:`numpy`: This import is used to access some Numpy dtype.


B. Constants
*************

Then, it is required to define some constants.

.. code-block:: python

    HOP_LENGTH = 128
    RATE = 16000
    NUM_SOURCES = 1
    PERIODS = 10

* :code:`PERIODS`: Indicates the buffer size of the PCM instances to prevent sound glitches. You can lower the value to
  reduce latency.


C. Main Function
*****************

Then, the main function initialize the sound cards and pipeline. Then, it performs sound source separation.

.. code-block:: python

    def main():
        mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
        pipeline = SstDelaySumPipeline(mics, hop_length=HOP_LENGTH, num_sources=NUM_SOURCES)

        input_pcm = alsaaudio.PCM(
            alsaaudio.PCM_CAPTURE,
            alsaaudio.PCM_NORMAL,
            channels=len(mics),
            rate=RATE,
            format=alsaaudio.PCM_FORMAT_S32_LE,
            periodsize=HOP_LENGTH,
            periods=PERIODS,
            device='hw:CARD=SC16,DEV=0',
        )
        output_pcm = alsaaudio.PCM(
            alsaaudio.PCM_PLAYBACK,
            alsaaudio.PCM_NORMAL,
            channels=NUM_SOURCES,
            rate=RATE,
            format=alsaaudio.PCM_FORMAT_S32_LE,
            periodsize=HOP_LENGTH,
            periods=PERIODS,
            device='default',
        )

        # Buffer the output PCM
        for _ in range(PERIODS):
            output_pcm.write(np.zeros(NUM_SOURCES * HOP_LENGTH, dtype=np.int32).tobytes())

        while True:
            _length, input_data = input_pcm.read()

            # The dtype must match the input_pcm alsa format.
            input_audio = interleaved_pcm_to_numpy(input_data, len(mics), dtype=np.int32)
            result = pipeline.process(input_audio)

            most_energy_tracked_audio = get_most_energy_tracked_audio(result)

            # The dtype must match the output_pcm alsa format.
            output_data = numpy_to_interleaved_pcm(most_energy_tracked_audio, dtype=np.int32)
            output_pcm.write(output_data)

* :code:`alsaaudio.PCM(...)`: Creates the instance that read and write to the sound card data. If you use a SC-16F sound
  card, you can replace the :code:`device='hw:CARD=SC16,DEV=0'` with :code:`device='hw:CARD=SC16F,DEV=0'`. For other
  sound cards, you can get their name with the following command: :code:`arecord -l`. In addition, you must change the
  microphone array configuration (:code:`mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)`). For the SC-16F, it must be:
  :code:`mics = Mics(Mics.Hardware.SC16F)`.

* The :code:`for` loop writes zeros on the output PCM instance to fill the buffer.

* The :code:`while` loop read the input PCM instance, perform sound source separation of the dominant sound and write
  the result on the output PCM instance.

* :code:`get_most_energy_tracked_audio`: Examines the pipeline results to identify and return the most dominant tracked
  source data.

D. Get Most Energy Tracked Audio Function
******************************************

It is required to define the function that get the most dominant tracked source data.

.. code-block:: python

    def get_most_energy_tracked_audio(result: SstDelaySumPipelineResult) -> np.ndarray:
        if len(result.tracked_directions_by_index.items()) == 0:
            return result.audio[0:1]

        i, _ = max(result.tracked_directions_by_index.items(), key=lambda x: x[1].energy)
        return result.audio[i : i + 1]


Summary
********

This script:

1. Configures the SST delay-and-sum pipeline and the sound cards.

2. Processes the audio in chunks and performs sound source separation on each segment.

By running this script, you can perform real-time sound source separation of the most dominant tracked source, making it
a practical demonstration of PyODAS2 capabilities for online SSS tasks.

.. include:: ../../../examples/live/sst_delay_sum_example.py
   :literal:
