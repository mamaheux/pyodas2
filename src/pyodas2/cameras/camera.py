from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class Camera(ABC):
    """
    The base class of a camera class.
    """

    @abstractmethod
    def read(self) -> Tuple[bool, np.typing.NDArray[np.uint8]]:
        """
        Read the next video frame.

        :return: The read RGB video frame
        """

    @abstractmethod
    def __enter__(self) -> 'Camera':
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
