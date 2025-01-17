import os

# Disable numpy multithreading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import signal
import threading

import alsaaudio
import numpy as np
import pyqtgraph as pg

from pyodas2.cameras import CvCamera
from pyodas2.pcm import interleaved_pcm_to_numpy
from pyodas2.pipelines import AcousticImagePipeline
from pyodas2.utils import Mics
from pyodas2.visualization import AcousticImageWidget

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
CALIBRATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'acoustic_image_calibration.pickle')

HOP_LENGTH = 256
RATE = 16000


stop_requested = False


def video_thread_run(pipeline: AcousticImagePipeline, acoustic_image_widget: AcousticImageWidget):
    with CvCamera(width=IMAGE_WIDTH, height=IMAGE_HEIGHT) as camera:
        while not stop_requested:
            ok, rgb_image = camera.read()
            if ok:
                acoustic_image = pipeline.generate_acoustic_image()
                acoustic_image_widget.set_images(rgb_image, acoustic_image)


def audio_thread_run(mics: Mics, pipeline: AcousticImagePipeline):
    pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                        channels=len(mics), rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                        periodsize=HOP_LENGTH, device='hw:CARD=SC16,DEV=0')

    while not stop_requested:
        length, data = pcm.read()
        if length < 0:
            continue

        audio = interleaved_pcm_to_numpy(data, len(mics), dtype=np.int32) # The dtype must match the alsa format.
        pipeline.process(audio)


def main():
    _app = pg.mkQApp("PyODAS2 - Acoustic Image Example")
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = AcousticImagePipeline(mics, CALIBRATION_PATH, IMAGE_WIDTH, IMAGE_HEIGHT, hop_length=HOP_LENGTH)

    acoustic_image_widget = AcousticImageWidget()
    acoustic_image_widget.show()

    video_thread = threading.Thread(target=video_thread_run, args=[pipeline, acoustic_image_widget])
    video_thread.start()

    audio_thread = threading.Thread(target=audio_thread_run, args=[mics, pipeline])
    audio_thread.start()

    try:
        pg.exec()
    finally:
        global stop_requested
        stop_requested = True
        video_thread.join()
        audio_thread.join()


if __name__ == '__main__':
    main()
