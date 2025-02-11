import pickle
import threading
from os import PathLike
from typing import Union

import numpy as np

from pyodas2.signals import Covs, Freqs, Hops, Masks
from pyodas2.systems import Scm, Stft, Window
from pyodas2.utils import Mics


class AcousticImagePipeline:
    """
    This is a class performing acoustic image generation.
    """

    def __init__(
        self,
        mics: Mics,
        calibration_path: Union[str, PathLike],
        image_width: int,
        image_height: int,
        hop_length: int = 128,
        n_fft: int = 512,
        fft_window: Window = Window.HANN,
        scm_alpha: float = 0.5,
    ) -> None:
        """
        Create a new acoustic image pipeline.

        :param mics: The microphone positions and directions of the microphone array
        :param hop_length: The number of samples in each processed audio frame, also named num_shifts. It must be at most equal equal to n_fft / 2.
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param scm_alpha: The alpha value to compute the spatial covariance matrix.
        """
        if hop_length > n_fft // 2:
            msg = 'hop_length must be at most n_fft // 2.'
            raise ValueError(msg)

        self._num_channels = len(mics)
        self._num_bins = n_fft // 2 + 1

        self._hops_in = Hops('xs', self._num_channels, hop_length)
        self._freqs_in = Freqs('Xs', self._num_channels, self._num_bins)
        self._masks = Masks('Ms', self._num_channels, self._num_bins)
        self._covs = Covs('XXs', self._num_channels, self._num_bins)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)

        self._masks.set_ones()

        self._image_width = image_width
        self._image_height = image_height

        with open(calibration_path, 'rb') as f:
            calibration = pickle.load(f)

        if calibration['num_channels'] != self._num_channels:
            msg = 'The calibration num_channels value differs from the provided one.'
            raise ValueError(msg)
        if calibration['n_fft'] != n_fft:
            msg = 'The calibration n_fft value differs from the provided one.'
            raise ValueError(msg)
        if calibration['image_width'] != self._image_width:
            msg = 'The calibration image_width value differs from the provided one.'
            raise ValueError(msg)
        if calibration['image_height'] != self._image_height:
            msg = 'The calibration image_height value differs from the provided one.'
            raise ValueError(msg)

        self._averaged_scm_lock = threading.Lock()
        self._averaged_scm = np.zeros(self._num_bins * self._covs.num_pairs)
        self._scm_alpha = scm_alpha
        self._vh = calibration['vh'].astype(np.complex64)
        self._d = calibration['d'].astype(np.complex64)

    def process(self, audio: np.ndarray) -> None:
        """
        Process the current audio frame

        :param audio: The audio data having the shape (len(mics), hop_length)
        """
        self._hops_in.load_numpy(audio)

        self._stft.process(self._hops_in, self._freqs_in)
        self._scm.process(self._freqs_in, self._masks, self._covs)

        with self._averaged_scm_lock:
            self._averaged_scm = (
                1.0 - self._scm_alpha
            ) * self._averaged_scm + self._scm_alpha * self._covs.xcorrs_to_numpy().flatten()

    def generate_acoustic_image(self, relative: bool = False) -> np.typing.NDArray[np.uint8]:
        """
        Generates an acoustic image using the last processed audio frame.

        :param relative: If True, return an acoustic image relative to minimum and maximum energy levels
        :return: The generated acoustic image.
        """
        with self._averaged_scm_lock:
            normalized_scm_array = self._averaged_scm / (np.abs(self._averaged_scm) + 1e-9)

        z = self._vh @ normalized_scm_array
        acoustic_image = np.real(self._d @ z) / self._vh.shape[1]
        acoustic_image = acoustic_image.reshape(self._image_width, self._image_height).T

        if relative:
            min_value = np.min(acoustic_image)
            max_value = np.max(acoustic_image)
            acoustic_image = (acoustic_image - min_value) / (max_value - min_value + 1e-9)
        else:
            acoustic_image = np.clip(acoustic_image, a_min=0.0, a_max=1.0)

        return (acoustic_image * 255).astype(np.uint8)
