6. Sound Source Separation (SSS) Using the Delay and Sum Beamformer and Tracked Sources
########################################################################################

This tutorial demonstrates how to use the PyODAS2 library to perform Sound Source Tracking (SST) and Sound Source
Separation (SSS) with the delay-and-sum beamformer applied to the tracked sources, with a pre-recorded audio file as
input. SST identifies and tracks the movement of sound sources over time, providing continuous updates on their
direction. While Sound Source Separation (SSS) enhances the tracked audio sources.

Here's how it works in PyODAS2:

1. **Determine TDOAs (Time Differences of Arrival) between microphone pairs.** TDOA represents the time delay between
   the arrival of a sound at two microphones. As sound travels at a constant speed (e.g., the speed of sound in air),
   microphones placed at different positions will detect the sound at slightly different times. By examining these time
   delays between microphone pairs, the system can estimate the origin of the sound. This process involves accurately
   calculating these delays using methods like cross-correlation, which identifies the time shift where the signals from
   the two microphones are most closely aligned.

2. **Determine potential DOAs (Direction of Arrival) using a predefined geometry.** DOA indicates the direction
   from which a sound originates relative to the microphone array. The system utilizes the geometry of the microphone
   array and a predefined grid of potential sound source directions. By comparing the observed TDOAs from the previous
   step to theoretical delays calculated for each direction in the predefined grid, the system identifies the best
   match. This match determines the most likely direction of arrival for the sound. This method translates TDOA data
   into spatial directions by leveraging the physical arrangement of the microphone array and the modeled grid of
   possible directions.

3. **Track DOAs over time to identify sound sources.** Tracking involves analyzing changes in DOAs across consecutive
   time frames to associate each sound source, whether stationary or moving, with its direction over time. After
   determining the DOAs for individual audio frames, the system compares them across frames to identify consistent
   patterns. Advanced tracking algorithms leverage factors such as direction stability, energy levels, and proximity
   to accurately associate DOAs with specific sound sources. Each sound source is assigned a unique identifier, which is
   retained as long as the source remains active and detectable. The system continuously updates the source position
   and status in real time, accommodating movement.

4. **Determine TDOAs for the tracked source direction.** For each tracked source direction, the theoretical TDOA are
   computed.

5. **Apply the delay-and-sum beamformer.** The audio signals received by each microphone in the array are delayed by an
   amount determined in step 4. After delaying them, the signals are summed together, creating a composite signal that
   emphasizes the sounds that come from the tracked directions.


Below is a breakdown of the code.

A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import os
    import wave

    from pyodas2.pcm import interleaved_pcm_to_numpy, numpy_to_interleaved_pcm
    from pyodas2.pipelines import SstDelaySumPipeline, SstDelaySumPipelineResult
    from pyodas2.utils import Mics

Below is a description of the imports:

* :code:`os`, :code:`wave`: Standard libraries for handling file paths and WAV audio files.

* :code:`pyodas2.pcm.interleaved_pcm_to_numpy`: Converts interleaved PCM audio data into a NumPy array for processing.

* :code:`pyodas2.pcm.numpy_to_interleaved_pcm`: Converts a NumPy array into interleaved PCM audio data.

* :code:`pyodas2.pipelines.SstDelaySumPipeline`, :code:`SstDelaySumPipelineResult`: This pipeline performs sound source
  tracking and sound source separation applied to tracked source using the delay-and-sum beamformer.

* :code:`pyodas2.types.Xyz`: A class for representing directions.

* :code:`pyodas2.utils.Mics`: Provides microphone configurations, in this case, for the SC-16F microphone array.


B. Constants
*************

Then, it is required to define some constants.

.. code-block:: python

    INPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix_sc16f_sst_delay_sum.wav')
    OUTPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'output.wav')

    HOP_LENGTH = 128

    NUM_SOURCES = 1
    NUM_DIRECTIONS = 2
    NUM_TRACKS = 3

    OUTPUT_SAMPLE_WIDTH = 2

* :code:`INPUT_PATH`: Specifies the path to the input audio file, located in the audio folder relative to the script.
  This path can be modified to point to a different file as needed.

* :code:`OUTPUT_PATH`: Specifies the path to the output audio file, located in the audio folder relative to the
  script. This path can be modified to point to a different file as needed.

* :code:`HOP_LENGTH`: Defines the number of audio samples processed per iteration. A lower value gives higher temporal
  resolution but requires more processing power.

* :code:`NUM_SOURCES`: Defines the number of TDOAs.

* :code:`NUM_DIRECTIONS`: Defines the number of potential DOAs.

* :code:`NUM_TRACKS`: Defines the number of tracked DOAs. This constant defines the number of channels in the output
  file.

* :code:`OUTPUT_SAMPLE_WIDTH`: Defines the number of bytes per sample for the output file.


C. Main Function - Initialization
**********************************

The next step is to define a :code:`main` function to process the audio file. At the beginning of the function, the
audio files are opened, the microphone array geometry is selected, a SST delay-and-sum pipeline is created and some
constants are computed.

.. code-block:: python

    def main():
        with wave.open(INPUT_PATH, 'rb') as wave_reader, wave.open(OUTPUT_PATH, 'wb') as wave_writer:
            wave_writer.setnchannels(NUM_TRACKS)
            wave_writer.setsampwidth(OUTPUT_SAMPLE_WIDTH)
            wave_writer.setframerate(wave_reader.getframerate())

            mics = Mics(Mics.Hardware.SC16F)
            assert wave_reader.getnchannels() == len(mics)

            pipeline = SstDelaySumPipeline(
                mics, hop_length=HOP_LENGTH, num_sources=NUM_SOURCES, num_directions=NUM_DIRECTIONS, num_tracks=NUM_TRACKS
            )

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

* :code:`pipeline = SstDelaySumPipeline(...)`: Creates the SST delay-and-sum pipeline with the microphone array
  configuration, the hop length, the number of sources (TDOAs), the number of directions (potential DOAs) and the number
  of tracked source (tracked DOAs). For more information, you can consult
  :py:class:`pyodas2.pipelines.SstDelaySumPipeline`.

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

                display_result(result)
                wave_writer.writeframes(numpy_to_interleaved_pcm(result.audio, sample_width=OUTPUT_SAMPLE_WIDTH))



* :code:`data = wave_reader.readframes(HOP_LENGTH)`: Reads audio data a chunk of audio data from the file. If the chunk
  size is smaller than expected, it means that the end of file is reached, so the loop is terminated. Therefore, the end
  of the audio file is not be processed if the last chunk is less than :code:`data_size`.

* :code:`interleaved_pcm_to_numpy`: Converts interleaved PCM data (bytes) into a NumPy array for easier manipulation.

* :code:`pipeline.process(audio)`: Processes the audio data through the pipeline, returning the sound source tracking
  result and the separated audio data. The index of the tracked source direction indicates the channel of the source
  in the audio data.

* :code:`display_result(result)`: Displays the result in the terminal.

* :code:`wave_writer.writeframes(numpy_to_interleaved_pcm(result.audio, sample_width=OUTPUT_SAMPLE_WIDTH))`: Converts
  the NumPy array into interleaved PCM data (bytes) and writes the data into the output file.


E. Display Result Function
***************************

So, it is required to define the function that displays the result.

.. code-block:: python

    def display_result(result: SstDelaySumPipelineResult):
        print('Potential directions')
        for d in result.potential_directions:
            print(f'\tenergy: {d.energy}\tdirection: {d.coord}')

        print('Tracked directions')
        for i, d in result.tracked_directions_by_index.items():
            print(f'\tindex: {i}\tid: {d.tracking_id}\tenergy: {d.energy}\tdirection: {d.coord}')

        print()


F. Script Entry Point
**********************

The last step is to call the main function.

.. code-block:: python

    if __name__ == '__main__':
        main()


Results
********
This is an example of the output comparing the audio before and after applying the delay-and-sum beamformer.

TODO add audio files

Before:

.. raw:: html

    <audio controls>
      <source src="_static/tutorials/sst_delay_sum_before.wav" type="audio/wav">
      Your browser does not support the <code>audio</code> element.
    </audio>

After:

.. raw:: html

    <audio controls>
      <source src="_static/tutorials/sst_delay_sum_after.wav" type="audio/wav">
      Your browser does not support the <code>audio</code> element.
    </audio>


Summary
********

This script:

1. Loads an audio file.

2. Configures the SST/delay-and-sum pipeline for the SC-16F microphone array.

3. Processes the audio in chunks and performs sound source tracking and sound source separation on each segment.

4. Displays the potential and tracked directions along with their corresponding energy levels.

4. Writes the separated audio into an audio file.

By running this script, you can detect, localize, track and enhance sound sources in the input audio file, making it a
practical demonstration of PyODAS2 capabilities for offline SST and SSS tasks.

.. include:: ../../../examples/file/sst_delay_sum_example.py
   :literal:
