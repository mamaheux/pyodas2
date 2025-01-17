import os
import signal
import threading

import alsaaudio
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QApplication

from pyodas2.cameras import CvCamera
from pyodas2.pcm import interleaved_pcm_to_numpy
from pyodas2.pipelines import AcousticImageCalibrationPipeline
from pyodas2.utils import Mics
from pyodas2.visualization import AcousticImageCalibrationWidget

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
CALIBRATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'acoustic_image_calibration.pickle')

HOP_LENGTH = 256
RATE = 16000


stop_requested = False


def video_thread_run(pipeline: AcousticImageCalibrationPipeline,
                     acoustic_image_calibration_widget: AcousticImageCalibrationWidget):
    with CvCamera(width=IMAGE_WIDTH, height=IMAGE_HEIGHT) as camera:
        while not stop_requested and not pipeline.is_finished:
            ok, bgr_image = camera.read()
            if ok:
                acoustic_image_calibration_widget.set_camera_image(bgr_image)


def audio_thread_run(mics: Mics,
                     pipeline: AcousticImageCalibrationPipeline,
                     acoustic_image_calibration_widget: AcousticImageCalibrationWidget,
                     app: QApplication):
    pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                        channels=len(mics), rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                        periodsize=HOP_LENGTH, device='hw:CARD=SC16,DEV=0')

    while not stop_requested and not pipeline.is_finished:
        length, data = pcm.read()
        if length < 0:
            continue

        audio = interleaved_pcm_to_numpy(data, len(mics), dtype=np.int32) # The dtype must match the alsa format.
        pipeline.process(audio)

        if acoustic_image_calibration_widget.record_requested:
            pipeline.record_tdoas()
            acoustic_image_calibration_widget.set_targets(pipeline.targets, pipeline.current_target_index)

    if pipeline.is_finished:
        acoustic_image_calibration_widget.show_progress_dialog()
        pipeline.calibrate(acoustic_image_calibration_widget.update_process_dialog)
        app.exit()


def main():
    app = pg.mkQApp("PyODAS2 - Acoustic Image Calibration")
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = AcousticImageCalibrationPipeline(mics, CALIBRATION_PATH, IMAGE_WIDTH, IMAGE_HEIGHT, hop_length=HOP_LENGTH)

    acoustic_image_calibration_widget = AcousticImageCalibrationWidget()
    acoustic_image_calibration_widget.set_targets(pipeline.targets, pipeline.current_target_index)
    acoustic_image_calibration_widget.show()

    video_thread = threading.Thread(target=video_thread_run, args=[pipeline, acoustic_image_calibration_widget])
    video_thread.start()

    audio_thread = threading.Thread(target=audio_thread_run, args=[mics, pipeline, acoustic_image_calibration_widget, app])
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
