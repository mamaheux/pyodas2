from typing import Tuple, cast

import cv2
import numpy as np

try:
    from libcamera import controls
    from picamera2 import Picamera2

    PICAMERA2_FOUND = True
except ImportError:
    PICAMERA2_FOUND = False

from .camera import Camera


class PiCamera(Camera):
    """
    A class to capture camera images using the picamera2 API. This API only works on Raspberry Pi computers.
    """

    def __init__(
        self,
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
    ):
        """
        Creates a new instance of PiCamera.

        :param device_index: The camera index.
        :param width: The image width
        :param height: The image height
        """
        if not PICAMERA2_FOUND:
            msg = 'Picamera2 is not supported or is not installed for your device.'
            raise NotImplementedError(msg)

        self._picam2 = Picamera2(device_index)
        config = self._picam2.create_preview_configuration({'size': (width, height), 'format': 'BGR888'})
        self._picam2.configure(config)

    def read(self) -> Tuple[bool, np.typing.NDArray[np.uint8]]:
        """
        Read the next video frame.

        :return: The read RGB video frame
        """
        bgr = self._picam2.capture_array()
        return True, cast(np.typing.NDArray[np.uint8], cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def __enter__(self) -> Camera:
        self._picam2.start()
        self._picam2.set_controls({'AfMode': controls.AfModeEnum.Manual, 'LensPosition': 0.0})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._picam2.stop()
        self._picam2.close()
