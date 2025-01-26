5. Sound Source Separation (SSS) Using Delay and Sum Beamformer Given a Direction
##################################################################################

The delay-and-sum beamformer works by taking signals from multiple microphones (or sensors) and applying time delays to
each microphone’s signal to align them in such a way that sound from a specific direction is reinforced, while sounds
from other directions are minimized. This process effectively "focuses" the microphone array on a particular sound
source, improving the signal-to-noise ratio for sounds from that direction and reducing interference from others.
It’s commonly used in applications like speech recognition, conference systems, and directional hearing aids.

This tutorial demonstrates how to perform Sound Source Separation (SSS) using the delay-and-sum beamformer to amplify
the sounds that come from given directions. Here's how it works in PyODAS2:

1. **Determine TDOAs (Time Differences of Arrival) between microphone pairs.** TDOA represents the time delay between
   the arrival of a sound at two microphones. As sound travels at a constant speed (e.g., the speed of sound in air),
   microphones placed at different positions will detect the sound at slightly different times. For each given
   direction, the theoretical TDOA are computed.

2. **Apply the delay-and-sum beamformer.** The audio signals received by each microphone in the array are delayed by the
   amount determined in step 1. After delaying them, the signals are summed together, creating a composite signal that
   emphasizes the sounds that come from the given directions.


Below is a breakdown of the code.

A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import os
    import wave

    from pyodas2.pcm import interleaved_pcm_to_numpy, numpy_to_interleaved_pcm
    from pyodas2.pipelines import SteeringDelaySumPipeline
    from pyodas2.types import Xyz
    from pyodas2.utils import Mics

Below is a description of the imports:

* :code:`os`, :code:`wave`: Standard libraries for handling file paths and WAV audio files.

* :code:`pyodas2.pcm.interleaved_pcm_to_numpy`: Converts interleaved PCM audio data into a NumPy array for processing.

* :code:`pyodas2.pcm.numpy_to_interleaved_pcm`: Converts a NumPy array into interleaved PCM audio data.

* :code:`pyodas2.pipelines.SteeringDelaySumPipeline`: This pipeline performs sound source separation for given
  directions using the delay-and-sum beamformer.

* :code:`pyodas2.types.Xyz`: A class for representing directions.

* :code:`pyodas2.utils.Mics`: Provides microphone configurations, in this case, for the SC-16F microphone array.


B. Constants
*************

Then, it is required to define some constants.

.. code-block:: python

    INPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix_sc16f.wav')
    OUTPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'output.wav')

    HOP_LENGTH = 128
    NUM_SOURCES = 1

    OUTPUT_SAMPLE_WIDTH = 2

* :code:`INPUT_PATH`: Specifies the path to the input audio file, located in the audio folder relative to the script.
  This path can be modified to point to a different file as needed.

* :code:`OUTPUT_PATH`: Specifies the path to the output audio file, located in the audio folder relative to the
  script. This path can be modified to point to a different file as needed.

* :code:`HOP_LENGTH`: Defines the number of audio samples processed per iteration. A lower value gives higher temporal
  resolution but requires more processing power.

* :code:`NUM_SOURCES`: Defines the number of audio source that will be separated by the delay-and-sum beamformer. A
  value other than 1 is not recommended.

* :code:`OUTPUT_SAMPLE_WIDTH`: Defines the number of bytes per sample for the output file.


C. Main Function - Initialization
**********************************

The next step is to define a :code:`main` function to process the audio file. At the beginning of the function, the
audio files are opened, the microphone array geometry is selected, a steering delay-and-sum pipeline is created and some
constants are computed.

.. code-block:: python

    def main():
        with wave.open(INPUT_PATH, 'rb') as wave_reader, wave.open(OUTPUT_PATH, 'wb') as wave_writer:
            wave_writer.setnchannels(NUM_SOURCES)
            wave_writer.setsampwidth(OUTPUT_SAMPLE_WIDTH)
            wave_writer.setframerate(wave_reader.getframerate())

            mics = Mics(Mics.Hardware.SC16F)
            assert wave_reader.getnchannels() == len(mics)

            pipeline = SteeringDelaySumPipeline(mics, hop_length=HOP_LENGTH, num_sources=NUM_SOURCES)
            pipeline.set_directions([Xyz(0.0, 0.0, 1.0)])

            data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()


* :code:`with wave.open(INPUT_PATH, 'rb') as wave_reader, wave.open(OUTPUT_PATH, 'wb') as wave_writer:`: Using a context
  manager, opens the input audio file in read-binary ('rb') mode and the output audio file in write-binary ('wb').

* :code:`wave_writer.setnchannels(NUM_SOURCES)`: Configures the number of channels for the output audio file.

* :code:`wave_writer.setsampwidth(NUM_SOURCES)`: Configures the number of bytes per sample for the output audio file.

* :code:`wave_writer.setframerate(NUM_SOURCES)`: Configures the sample rate for the output audio file.

* :code:`mics = Mics(Mics.Hardware.SC16F)`: Creates the SC-16F microphone array configuration. All the available
  configurations are listed in :py:class:`pyodas2.utils.Mics.Hardware`. Also, it is possible to pass a list of
  :py:class:`pyodas2.utils.Mic`.

* :code:`assert wave_reader.getnchannels() == len(mics)`: Ensures that the number of microphones in the array is the
  same as the number of channels in the audio file.

* :code:`pipeline = SteeringDelaySumPipeline(...)`: Creates the steering delay-and-sum pipeline with the microphone array
  configuration, the hop length and the number of sources (TDOAs). For more information, you can consult
  :py:class:`pyodas2.pipelines.SteeringDelaySumPipeline`.

* :code:`pipeline.set_directions([Xyz(0.0, 0.0, 1.0)])`: Specifies the direction for performing sound source separation.
  The number of directions must correspond to the value of :code:`NUM_SOURCES`. The directions can be updated at any
  time.

* :code:`data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()`: Computes the expected number
  of bytes for each chunk of data.


D. Main Function - Processing
******************************

Then, the audio is processed chunk by chunk.

.. code-block:: python

            while True:
                data = wave_reader.readframes(HOP_LENGTH)
                if len(data) != data_size:
                    break

                audio = interleaved_pcm_to_numpy(data, wave_reader.getnchannels(), sample_width=wave_reader.getsampwidth())
                result = pipeline.process(audio)
                wave_writer.writeframes(numpy_to_interleaved_pcm(result.audio, OUTPUT_SAMPLE_WIDTH))

* :code:`data = wave_reader.readframes(HOP_LENGTH)`: Reads audio data a chunk of audio data from the file. If the chunk
  size is smaller than expected, it means that the end of file is reached, so the loop is terminated. Therefore, the end
  of the audio file is not be processed if the last chunk is less than :code:`data_size`.

* :code:`interleaved_pcm_to_numpy`: Converts interleaved PCM data (bytes) into a NumPy array for easier manipulation.

* :code:`pipeline.process(audio)`: Processes the audio data through the pipeline, returning the separated audio data.

* :code:`wave_writer.writeframes(numpy_to_interleaved_pcm(result.audio, sample_width=OUTPUT_SAMPLE_WIDTH))`: Converts
  the NumPy array into interleaved PCM data (bytes) and writes the data into the output file.


E. Script Entry Point
**********************

The last step is to call the main function.

.. code-block:: python

    if __name__ == '__main__':
        main()


Results
********
This is an example of the output comparing the audio before and after applying the delay-and-sum beamformer.

TODO add audio files


Summary
********

.. include:: ../../../examples/file/steering_delay_sum_example.py
   :literal:

1. Loads an audio file.

2. Configures the delay-and-sum pipeline for the SC-16F microphone array and a given direction.

3. Processes the audio in chunks and performs sound source separation on each segment.

4. Writes the separated audio into an audio file.

By running this script, you can perform sound source separation for given directions in the input audio file, making it
a practical demonstration of PyODAS2 capabilities for offline SSS tasks.

.. include:: ../../../examples/file/delay_sum_example.py
   :literal:
