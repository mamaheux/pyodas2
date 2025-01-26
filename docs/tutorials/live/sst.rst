3. Sound Source Tracking (SST)
###############################

This tutorial assumes that you have already gone through this :doc:`one <../file/sst>`. This tutorial shows how to
visualize sound source tracking results in real time.

Below is a breakdown of the code.


A. Imports
***********

First, you have to add some import statements.

.. code-block:: python

    import signal
    import threading

    import alsaaudio
    import numpy as np
    import pyqtgraph as pg

    from pyodas2.pcm import interleaved_pcm_to_numpy
    from pyodas2.pipelines import SstPipeline
    from pyodas2.utils import Mics
    from pyodas2.visualization import ElevationAzimuthWidget, SourceLocationWidget

Compared to the pre-recorded tutorial, the following imports are also required:

* :code:`signal`, :code:`threading`: Standard libraries for handling signals and thread.

* :code:`alsaaudio`: Handles sound cards on Linux.

* :code:`numpy`: This import is used to access some Numpy dtype.

* :code:`pyqtgraph`, :code:`pyodas2.visualization.ElevationAzimuthWidget` and
  :code:`pyodas2.visualization.SourceLocationWidget`: Handles displaying the sound source tracking results.


B. Constants
*************

Then, it is required to define some constants.

.. code-block:: python

    HOP_LENGTH = 256
    RATE = 16000


C. Audio Thread
****************

In order to process the audio data that comes from the sound card, another thread is required, while the main thread
handle the graphical interface.

.. code-block:: python

    stop_requested = False


    def audio_thread_run(elevation_azimuth_widget: ElevationAzimuthWidget, source_location_widget: SourceLocationWidget):
        mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
        pipeline = SstPipeline(mics, sample_rate=RATE, hop_length=HOP_LENGTH)

        pcm = alsaaudio.PCM(
            alsaaudio.PCM_CAPTURE,
            alsaaudio.PCM_NORMAL,
            channels=len(mics),
            rate=RATE,
            format=alsaaudio.PCM_FORMAT_S32_LE,
            periodsize=HOP_LENGTH,
            device='hw:CARD=SC16,DEV=0',
        )

        while not stop_requested:
            length, data = pcm.read()
            if length < 0:
                continue

            # The dtype must match the alsa format.
            audio = interleaved_pcm_to_numpy(data, len(mics), dtype=np.int32)
            result = pipeline.process(audio)

            elevation_azimuth_widget.add_potential_sources(result.potential_directions)
            elevation_azimuth_widget.add_tracked_sources(result.tracked_directions_by_index)

            source_location_widget.set_potential_sources(result.potential_directions)
            source_location_widget.set_tracked_sources(result.tracked_directions_by_index)

* :code:`stop_requested`: This is a variable to stop the audio processing when the graphical interface closes.

* :code:`alsaaudio.PCM(...)`: Creates the instance that read the sound card data. If you use a SC-16F sound card, you
  can replace the :code:`device='hw:CARD=SC16,DEV=0'` with :code:`device='hw:CARD=SC16F,DEV=0'`. For other sound cards,
  you can get their name with the following command: :code:`arecord -l`. In addition, you must change the microphone
  array configuration (:code:`mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)`). For the SC-16F, it must be:
  :code:`mics = Mics(Mics.Hardware.SC16F)`.

* :code:`pcm.read()`: Reads the next available audio data.

* :code:`interleaved_pcm_to_numpy(data, len(mics), dtype=np.int32)`: Converts interleaved PCM data (bytes) into a NumPy
  array for easier manipulation. The :code:`dtype` must match the alsa format.

* :code:`elevation_azimuth_widget.add_potential_sources(result.directions)` and
  :code:`source_location_widget.set_potential_sources(result.directions)` update the graphical interfaces with the new
  potential sources.

* :code:`elevation_azimuth_widget.add_tracked_sources(result.directions)` and
  :code:`source_location_widget.set_tracked_sources(result.directions)` update the graphical interfaces with the new
  tracked sources.


D. Main Function
*****************

Then, the main function initialize the graphical interfaces, the audio thread and execute the graphical interface
application.

.. code-block:: python

    def main():
        _app = pg.mkQApp('PyODAS2 - SST Example')
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        elevation_azimuth_widget = ElevationAzimuthWidget(sample_rate=RATE, hop_length=HOP_LENGTH)
        elevation_azimuth_widget.show()

        source_location_widget = SourceLocationWidget()
        source_location_widget.show()

        audio_thread = threading.Thread(target=audio_thread_run, args=[elevation_azimuth_widget, source_location_widget])
        audio_thread.start()

        try:
            pg.exec()
        finally:
            global stop_requested
            stop_requested = True
            audio_thread.join()

* `signal.signal(signal.SIGINT, signal.SIG_DFL)`: Enables the functionality of :code:`CTRL-C`.

* Once the graphical interface application ends (:code:`pg.exec()`), the audio thread is stopped.


E. Script Entry Point
**********************

The last step is to call the main function.

.. code-block:: python

    if __name__ == '__main__':
        main()

Results
********
This is an example of the output shown by the widgets. The first widget displays the directions over time, while the
second shows the directions in 3D, in real-time. The potential sources and tracked source are in blue and red,
respectively.

.. image:: ../../_static/tutorials/live/sst.png


Summary
********

This script:

1. Processes real-time audio data from a sound card.

2. Displays the potential and tracked directions on a graphical interface.

By running this script, you can detect and localize sound sources in real-time, making it a practical demonstration of
PyODAS2 capabilities for online SSL tasks.

.. include:: ../../../examples/live/sst_example.py
   :literal:
