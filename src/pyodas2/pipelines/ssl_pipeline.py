from dataclasses import dataclass
from typing import List

import numpy as np

from pyodas2.signals import Covs, Doas, Freqs, Hops, Masks, Tdoas
from pyodas2.systems import Gcc, Phat, Scm, Ssl, Stft, Window
from pyodas2.utils import Mics, Points


@dataclass
class SslPipelineResult:
    """
    This is a class representing the results of the sound source localization
    """
    directions: List[Doas.Dir]


class SslPipeline:
    """
    This is a class performing sound source localization.
    """

    def __init__(self,
                 mics: Mics,
                 sample_rate: float = 16000,
                 hop_length: int = 128,
                 num_sources: int = 1,
                 num_directions: int = 2,
                 n_fft: int = 512,
                 fft_window: Window = Window.HANN,
                 sound_speed: float = 343.0,
                 ssl_geometry: Points.Geometry = Points.Geometry.HALFSPHERE,
                 scm_alpha: float = 0.5):
        """
        Create a new sound source localization pipeline.

        :param mics: The microphone positions and directions of the microphone array.
        :param sample_rate: The sample rate of the sound.
        :param hop_length: The number of samples in each processed audio frame, also named num_shifts.
        :param num_sources: The number of audio source.
        :param num_directions: TODO num_directions vs num_sources
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param sound_speed: The speed of sound in m/s.
        :param ssl_geometry: The geometry to perform the sound source localisation.
        :param scm_alpha: TODO
        """

        self._num_channels = len(mics)
        self._num_bins = n_fft // 2 + 1
        self._points = Points(ssl_geometry)

        self._hops = Hops("xs", self._num_channels, hop_length)
        self._freqs = Freqs("Xs", self._num_channels, self._num_bins)
        self._masks = Masks("Ms", self._num_channels, self._num_bins)
        self._covs = Covs("XXs", self._num_channels, self._num_bins)
        self._covs_phat = Covs("XXps", self._num_channels, self._num_bins)
        self._tdoas = Tdoas("tdoas", self._num_channels, num_sources)
        self._doas = Doas("doas", num_directions)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)
        self._phat = Phat(self._num_channels, self._num_bins)
        self._gcc = Gcc(num_sources, self._num_channels, self._num_bins)
        self._ssl = Ssl(mics, self._points, sample_rate, sound_speed, num_sources, num_directions)

        self._masks.set_ones()

    def process(self, audio: np.ndarray) -> SslPipelineResult:
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
        self._ssl.process(self._tdoas, self._doas)

        return SslPipelineResult([d.copy() for d in self._doas if d.type == Doas.Src.POTENTIAL])
