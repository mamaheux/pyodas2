from typing import Tuple, cast

import cv2
import numpy as np

from .camera import Camera

CV_YUV_FOURCC = cv2.VideoWriter.fourcc('V', 'Y', 'U', 'Y')
CV_MJPG_FOURCC = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')


class CvCamera(Camera):
    def __init__(self,
                 device_index: int = 0,
                 width: int = 640,
                 height: int = 480,
                 fourcc: int = CV_YUV_FOURCC,
                 fps: float = 30.0):
        self._video_capture = cv2.VideoCapture(device_index)

        self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._video_capture.set(cv2.CAP_PROP_FOURCC, fourcc)
        self._video_capture.set(cv2.CAP_PROP_FPS, fps)

        self._video_capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self._video_capture.set(cv2.CAP_PROP_FOCUS, 0)

    def set(self, prop_id: int, value: float):
        self._video_capture.set(prop_id, value)

    def read(self) -> Tuple[bool, np.typing.NDArray[np.uint8]]:
        ok, bgr = self._video_capture.read()
        return ok, cast(np.typing.NDArray[np.uint8], cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._video_capture.release()
