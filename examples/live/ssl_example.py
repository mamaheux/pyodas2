"""
This is an example to illustrate how to perform sound source localization using a live audio stream.
"""

import threading
import signal

import alsaaudio
import numpy as np

import pyqtgraph as pg

from pyodas2.utils import Mics
from pyodas2.pipelines import SslPipeline
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
        l, data = pcm.read()
        if l < 0:
            continue

        audio = np.frombuffer(data, dtype=np.int32).reshape(-1, len(mics)).T
        result = pipeline.process(audio)

        elevation_azimuth_widget.add_potential_sources(result.directions)
        source_location_widget.set_potential_sources(result.directions)


def main():
    app = pg.mkQApp("PyODAS2 - SSL Example")
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
