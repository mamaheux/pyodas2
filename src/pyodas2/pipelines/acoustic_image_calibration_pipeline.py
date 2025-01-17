import pickle
from itertools import product
from os import PathLike
from typing import Callable, Union, cast

import numpy as np

from pyodas2.signals import Covs, Freqs, Hops, Masks, Tdoas
from pyodas2.systems import Gcc, Phat, Scm, Stft, Window
from pyodas2.utils import Mics


class AcousticImageCalibrationPipeline:
    """
    This is a class performing acoustic image calibration.
    """

    def __init__(self,
                 mics: Mics,
                 calibration_path: Union[str, PathLike],
                 image_width: int,
                 image_height: int,
                 hop_length: int = 128,
                 n_fft: int = 512,
                 fft_window: Window = Window.HANN,
                 scm_alpha: float = 0.5,
                 target_count: int = 5,
                 target_margin: int = 20,
                 polynomial_order: int = 3,
                 svd_phat_batch_size: int = 1000,
                 svd_phat_delta: float = 1e-3) -> None:
        """
        Create a new acoustic image calibration pipeline.

        :param mics: The microphone positions and directions of the microphone array.
        :param calibration_path: The calibration output path.
        :param image_width: The camera image width.
        :param image_height: The camera image height.
        :param hop_length: The number of samples in each processed audio frame, also named num_shifts.
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param scm_alpha: TODO The
        :param target_count: The number of target per axis.
        :param target_margin: The target margin in pixels.
        :param polynomial_order: TODO a
        :param svd_phat_batch_size: TODO a
        :param svd_phat_delta: TODO a
        """
        if image_width < 2 * target_margin or image_height < 2 * target_margin:
            msg = f'The image width and image height must be greater than {2 * target_margin}.'
            raise ValueError(msg)
        if target_count**2 < (polynomial_order + 1)**2:
            msg = 'There are not enough target for the polynomial_order.'
            raise ValueError(msg)

        self._num_channels = len(mics)
        self._n_fft = n_fft
        self._num_bins = n_fft // 2 + 1
        self._num_sources = 1

        self._hops = Hops("xs", self._num_channels, hop_length)
        self._freqs = Freqs("Xs", self._num_channels, self._num_bins)
        self._masks = Masks("Ms", self._num_channels, self._num_bins)
        self._covs = Covs("XXs", self._num_channels, self._num_bins)
        self._covs_phat = Covs("XXps", self._num_channels, self._num_bins)
        self._tdoas = Tdoas("tdoas", self._num_channels, self._num_sources)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)
        self._phat = Phat(self._num_channels, self._num_bins)
        self._gcc = Gcc(self._num_sources, self._num_channels, self._num_bins)

        self._masks.set_ones()

        self._calibration_path = calibration_path
        self._image_width = image_width
        self._image_height = image_height
        self._target_count = target_count
        self._target_margin = target_margin
        self._polynomial_order = polynomial_order
        self._svd_phat_batch_size = svd_phat_batch_size
        self._svd_phat_delta = svd_phat_delta

        self._targets = self._generate_targets()
        self._current_target_index = 0

        self._target_tdoas = np.zeros((self._targets.shape[0], self._tdoas.num_pairs), dtype=float)

    def _generate_targets(self) -> np.typing.NDArray[int]:
        x_values = np.linspace(self._target_margin, self._image_width - self._target_margin, self._target_count, dtype=int)
        y_values = np.linspace(self._target_margin, self._image_height - self._target_margin, self._target_count, dtype=int)
        return cast(np.typing.NDArray[int], np.array(np.meshgrid(x_values, y_values)).T.reshape(-1, 2))

    @property
    def targets(self) -> np.typing.NDArray[int]:
        return self._targets

    @property
    def current_target_index(self) -> int:
        return self._current_target_index

    @property
    def is_finished(self) -> bool:
        return self._current_target_index >= self._targets.shape[0]

    def process(self, audio: np.typing.NDArray) -> None:
        """
        Process the current audio frame

        :param audio: The audio data having the shape (len(mics), hop_length)
        :return: The result for the current audio frame
        """
        self._hops.load_numpy(audio)

        self._stft.process(self._hops, self._freqs)
        self._scm.process(self._freqs, self._masks, self._covs)
        self._phat.process(self._covs, self._covs_phat)
        self._gcc.process(self._covs_phat, self._tdoas)

    def record_tdoas(self) -> None:
        for i in range(self._tdoas.num_pairs):
            self._target_tdoas[self._current_target_index, i] = self._tdoas[0, i].delay

        self._current_target_index += 1

    def calibrate(self, progress_callback: Callable[[int, int], None]) -> None:
        """
        Performs the calibration process.
        :param progress_callback: A process callback
        """
        a_inv = self._compute_a_inv()
        c = a_inv @ self._target_tdoas
        image_delays = self._compute_image_delays(c)
        d, vh = self._compute_svd_phat(image_delays, progress_callback)

        calibration = {
            'num_channels': self._num_channels,
            'n_fft': self._n_fft,
            'image_width': self._image_width,
            'image_height': self._image_height,
            'c': c,
            'image_delays': image_delays,
            'd': d,
            'vh': vh
        }
        with open(self._calibration_path, 'wb') as f:
            pickle.dump(calibration, f)

    def _compute_a_inv(self) -> np.ndarray:
        normalized_x = (2 * self._targets[:, 0] - self._image_width - 1) / (self._image_width - 1)
        normalized_y = (2 * self._targets[:, 1] - self._image_height - 1) / (self._image_height - 1)
        exponents = np.array([[x, y] for x, y in product(range(self._polynomial_order + 1), repeat=2)])

        a = normalized_x ** exponents[:, 0][:, np.newaxis] * normalized_y ** exponents[:, 1][:, np.newaxis]
        return np.linalg.solve(a @ a.T, a)

    def _compute_image_delays(self, c: np.ndarray) -> np.ndarray:
        x = np.arange(self._image_width, dtype=int)
        y = np.arange(self._image_height, dtype=int)
        pixels = np.array(np.meshgrid(x, y)).T.reshape(-1, 2)

        normalized_x = (2 * pixels[:, 0] - self._image_width - 1) / (self._image_width - 1)
        normalized_y = (2 * pixels[:, 1] - self._image_height - 1) / (self._image_height - 1)
        exponents = np.array([[x, y] for x, y in product(range(self._polynomial_order + 1), repeat=2)])

        a = normalized_x ** exponents[:, 0][:, np.newaxis] * normalized_y ** exponents[:, 1][:, np.newaxis]
        return a.T @ c

    def _compute_svd_phat(self, delays: np.ndarray, progress_callback: Callable[[int, int], None]):
        n_points, n_pairs = delays.shape
        bins_indices = np.tile(
            np.arange(0, self._num_bins) / self._n_fft, (n_pairs, 1)
        )
        Ws = np.zeros((self._svd_phat_batch_size, self._num_bins * n_pairs), dtype=np.complex64)

        # From https://github.com/introlab/pyodas/blob/main/library/pyodas/src/pyodas/core/svd_phat.py#L160
        # First loop to calculate the appropriate K and obtain VH
        K = 0
        point_index = 0
        while point_index != n_points:
            points_index_range = self._svd_phat_batch_size - K
            if n_points < points_index_range + point_index:
                points_index_range = n_points - point_index

            batch_delays = delays[point_index : point_index + points_index_range, :]
            delays_multiplied_by_bins = np.einsum('ij, jk->ijk', batch_delays, bins_indices).reshape(points_index_range, -1)
            Ws[K : K + points_index_range, :] = np.exp(2j * np.pi * delays_multiplied_by_bins)

            _, S, VH = np.linalg.svd(Ws, full_matrices=False)

            r = np.cumsum(S ** 2, axis=0) / np.sum(S ** 2)
            K = max([np.argmax((r > (1.0 - self._svd_phat_delta)).astype(float)), K])

            S = S[:K].astype(np.complex64)
            VH = VH[:K, :]

            Ws[:] = 0.0
            Ws[:K, :] = np.diag(S) @ VH

            point_index += points_index_range

            progress_callback(point_index, 2 * n_points)

        # Second loop to obtain D
        D = np.zeros((n_points, K), dtype=np.complex64)
        point_index = 0
        while point_index != n_points:

            points_index_range = self._svd_phat_batch_size
            if n_points < points_index_range + point_index:
                points_index_range = n_points - point_index

            batch_delays = delays[
                           point_index : point_index + points_index_range, :
                           ]
            delays_multiplied_by_bins = np.einsum(
                "ij, jk->ijk", batch_delays, bins_indices
            ).reshape(points_index_range, -1)
            Ws[:points_index_range, :] = np.exp(
                2j * np.pi * delays_multiplied_by_bins
            )

            D[point_index : point_index + points_index_range, :] = (
                    Ws[:points_index_range, :] @ np.conj(VH).T
            )

            point_index += points_index_range

            progress_callback(n_points + point_index, 2 * n_points)

        return D, VH
