from typing import Tuple, cast

import cv2
import numpy as np

from .camera import Camera

CV_YUV_FOURCC = cv2.VideoWriter.fourcc('V', 'Y', 'U', 'Y')
CV_MJPG_FOURCC = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')


class CvCamera(Camera):
    """
    A class to capture camera images using the OpenCV API.
    """
    def __init__(self,
                 device_index: int = 0,
                 width: int = 640,
                 height: int = 480,
                 fourcc: int = CV_YUV_FOURCC,
                 fps: float = 30.0):
        """


        :param device_index: The camera index.
        :param width: The image width.
        :param height: The image height.
        :param fourcc: Defines how the capture is done. It may be `CV_YUV_FOURCC` or `CV_MJPG_FOURCC`.
        :param fps: The framerate at which the image are captured.
        """
        self._video_capture = cv2.VideoCapture(device_index)

        self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._video_capture.set(cv2.CAP_PROP_FOURCC, fourcc)
        self._video_capture.set(cv2.CAP_PROP_FPS, fps)

        self._video_capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self._video_capture.set(cv2.CAP_PROP_FOCUS, 0)

    def set(self, prop_id: int, value: float):
        """
        Sets a property in the underling OpenCV video capture instance.
        :param prop_id: The property id
        :param value: The property value
        """
        self._video_capture.set(prop_id, value)

    def read(self) -> Tuple[bool, np.typing.NDArray[np.uint8]]:
        """
        Read the next video frame.
        :return: The read RGB video frame
        """
        ok, bgr = self._video_capture.read()
        return ok, cast(np.typing.NDArray[np.uint8], cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._video_capture.release()
