"""
This is an example to illustrate how to perform sound source localization using a live audio stream.
"""

import signal
import threading

import alsaaudio
import numpy as np
import pyqtgraph as pg

from pyodas2.pcm import interleaved_pcm_to_numpy
from pyodas2.pipelines import SslPipeline
from pyodas2.utils import Mics
from pyodas2.visualization import ElevationAzimuthWidget, SourceLocationWidget

HOP_LENGTH = 256
RATE = 16000


stop_requested = False


def audio_thread_run(elevation_azimuth_widget: ElevationAzimuthWidget, source_location_widget: SourceLocationWidget):
    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = SslPipeline(mics, sample_rate=RATE, hop_length=HOP_LENGTH)

    pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                        channels=len(mics), rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                        periodsize=HOP_LENGTH, device='hw:CARD=SC16,DEV=0')

    while not stop_requested:
        length, data = pcm.read()
        if length < 0:
            continue

        audio = interleaved_pcm_to_numpy(data, len(mics), dtype=np.int32) # The dtype must match the alsa format.
        result = pipeline.process(audio)

        elevation_azimuth_widget.add_potential_sources(result.directions)
        source_location_widget.set_potential_sources(result.directions)


def main():
    _app = pg.mkQApp("PyODAS2 - SSL Example")
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


if __name__ == '__main__':
    main()
