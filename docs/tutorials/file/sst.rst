3. Sound Source Tracking (SST)
###############################

This tutorial demonstrates how to perform Sound Source Tracking (SST) using the PyODAS2 library, with a pre-recorded
audio file as input. SST identifies and tracks the movement of sound sources over time, providing continuous updates on
their direction. Here's how it works in PyODAS2:

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

By default, PyODAS2 determines a single TDOA, two DOAs and three tracked DOAs. These numbers can be increased.

Below is a breakdown of the code.

A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import os
    import wave

    from pyodas2.pcm import interleaved_pcm_to_numpy
    from pyodas2.pipelines import SstPipeline, SstPipelineResult
    from pyodas2.utils import Mics

Below is a description of the imports:

* :code:`os`, :code:`wave`: Standard libraries for handling file paths and WAV audio files.

* :code:`pyodas2.pcm.interleaved_pcm_to_numpy`: Converts interleaved PCM audio data into a NumPy array for processing.

* :code:`pyodas2.pipelines.SstPipeline`, :code:`SstPipelineResult`: The SST pipeline performs sound source tracking, and
  the result object contains the potential directions and the tracked directions.

* :code:`pyodas2.utils.Mics`: Provides microphone configurations, in this case, for the SC-16F microphone array.


B. Constants
*************

Then, it is required to define some constants.

.. code-block:: python

    AUDIO_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix_sc16f.wav')
    HOP_LENGTH = 128

* :code:`AUDIO_PATH`: Specifies the path to the input audio file, located in the audio folder relative to the script.
  This path can be modified to point to a different file as needed.

* :code:`HOP_LENGTH`: Defines the number of audio samples processed per iteration. A lower value gives higher temporal
  resolution but requires more processing power.


C. Main Function - Initialization
**********************************

The next step is to define a :code:`main` function to process the audio file. At the beginning of the function,
the audio file is opened, the microphone array geometry is selected, a SST pipeline is created and some constants are
computed.

.. code-block:: python

    def main():
        with wave.open(AUDIO_PATH, 'rb') as wave_reader:
            mics = Mics(Mics.Hardware.SC16F)
            assert wave_reader.getnchannels() == len(mics)

            pipeline = SstPipeline(mics, sample_rate=wave_reader.getframerate(), hop_length=HOP_LENGTH)

            data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()

* :code:`with wave.open(AUDIO_PATH, 'rb') as wave_reader:`: Opens the audio file in read-binary ('rb') mode using a
  context manager.

* :code:`mics = Mics(Mics.Hardware.SC16F)`: Creates the SC-16F microphone array configuration. All the available
  configurations are listed in :py:class:`pyodas2.utils.Mics.Hardware`. Also, it is possible to pass a list of
  :py:class:`pyodas2.utils.Mic`.

* :code:`assert wave_reader.getnchannels() == len(mics)`: Ensures that the number of microphones in the array is the
  same as the number of channels in the audio file.

* :code:`pipeline = SstPipeline(...)`: Creates the SST pipeline with the microphone array configuration, the audio file
  sample rate and the hop length. The number of TDOAs, the number of potential DOAs and the number of tracked DOAs can
  be adjusted by the argument :code:`num_sources`, :code:`num_directions` and :code:`num_tracks`, respectively. The
  predefined grid of potential sound source directions can be adjusted using the argument :code:`ssl_geometry`.
  For more information, you can consult :py:class:`pyodas2.pipelines.SstPipeline`.

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

* :code:`data = wave_reader.readframes(HOP_LENGTH)`: Reads audio data a chunk of audio data from the file. If the chunk
  size is smaller than expected, it means that the end of file is reached, so the loop is terminated. Therefore, the end
  of the audio file is not be processed if the last chunk is less than :code:`data_size`.

* :code:`interleaved_pcm_to_numpy`: Converts interleaved PCM data (bytes) into a NumPy array for easier manipulation.

* :code:`pipeline.process(audio)`: Processes the audio data through the SST pipeline, returning the sound source
  tracking result.

* :code:`display_result(result)`: Displays the result in the terminal.


E. Display Result Function
***************************

It is required to define the function that displays the result.

.. code-block:: python

    def display_result(result: SstPipelineResult):
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
This is an example of the output.

.. code-block::

    ...
    Potential directions
            energy: 0.9755510091781616      direction: (0.882837,0.454678,0.117757)
            energy: 0.0044414205476641655   direction: (0.64684,0.681499,0.342282)
    Tracked directions
            index: 1        id: 2   energy: 0.9800000190734863      direction: (0.882162,0.455763,0.11862)

    Potential directions
            energy: 0.9754829406738281      direction: (0.882837,0.454678,0.117757)
            energy: 0.004479925148189068    direction: (0.64684,0.681499,0.342282)
    Tracked directions
            index: 1        id: 2   energy: 0.9800000190734863      direction: (0.882223,0.455665,0.118541)
    ...


Summary
**************

This script:

1. Loads an audio file.

2. Configures the SST pipeline for the SC-16F microphone array.

3. Processes the audio in chunks and performs sound source tracking on each segment.

4. Displays the potential and tracked directions along with their corresponding energy levels.

By running this script, you can detect, localize and track sound sources in the input audio file, making it a practical
demonstration of PyODAS2 capabilities for offline SST tasks.

.. include:: ../../../examples/file/sst_example.py
   :literal:
