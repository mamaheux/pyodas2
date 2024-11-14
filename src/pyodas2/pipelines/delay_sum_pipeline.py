from dataclasses import dataclass

import numpy as np

from pyodas2.utils import Mics, Points
from pyodas2.signals import Hops, Freqs, Masks, Covs, Tdoas, Weights
from pyodas2.systems import Stft, Window, Scm, Phat, Gcc, DelaySum, Beamformer, Istft


@dataclass
class DelaySumPipelineResult:
    """
    This is a class representing the results of the delay and sum beamforming
    """
    audio: np.ndarray[np.float32]


class DelaySumPipeline:
    """
    This is a class performing delay and sum beamforming.

                               Ms (all 1's)
                                     |
                                     *
    +----+   xs   +------+   Xs   +-----+   XXs   +------+   XXps   +---------+
    | In | -----* | STFT | -----* | SCM | ------* | PHAT | -------* | GCC/FCC |
    +----+        +------+   |    +-----+         +------+          +---------+
                             |                                           |
                             |             Ws      +----+      tdoas     |
                             |        +------------| DS | *--------------+
                             |        |            +----*
                             |        *
                             |    +-------+   Ys   +-------+   ys   +-----+
                             +--* | Bfmer | -----* | iSTFT | -----* | Out |
                                  +-------+        +-------+        +-----+
    """
    def __init__(self,
                 mics: Mics,
                 hop_length: int = 128,
                 num_sources: int = 1,
                 n_fft: int = 512,
                 fft_window: Window = Window.HANN,
                 scm_alpha: float = 0.5):
        """
        Create a new delay and sum pipeline.

        :param mics: The microphone positions and directions of the microphone array
        :param hop_length:
        :param num_sources: The number of samples in each processed audio frame, also named num_shifts.
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param scm_alpha: TODO
        """

        self._num_channels = len(mics)
        self._num_bins = n_fft // 2 + 1

        self._hops_in = Hops("xs", self._num_channels, hop_length)
        self._freqs_in = Freqs("Xs", self._num_channels, self._num_bins)
        self._masks = Masks("Ms", self._num_channels, self._num_bins)
        self._covs = Covs("XXs", self._num_channels, self._num_bins)
        self._covs_phat = Covs("XXps", self._num_channels, self._num_bins)
        self._tdoas = Tdoas("tdoas", self._num_channels, num_sources)
        self._weights = Weights("Ws", num_sources, self._num_channels, self._num_bins)
        self._freqs_out = Freqs("Ys", num_sources, self._num_bins)
        self._hops_out = Hops("ys", num_sources, hop_length)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)
        self._phat = Phat(self._num_channels, self._num_bins)
        self._gcc = Gcc(num_sources, self._num_channels, self._num_bins)
        self._delaysum = DelaySum(num_sources, self._num_channels, self._num_bins)
        self._beamformer = Beamformer(num_sources, self._num_channels, self._num_bins)
        self._istft = Istft(num_sources, n_fft, hop_length, fft_window)

        self._masks.set_ones()

    def process(self, audio: np.ndarray) -> DelaySumPipelineResult:
        """
        Process the current audio frame

        :param audio: The audio data having the shape (len(mics), hop_length)
        :return: The result for the current audio frame
        """
        self._hops_in.load_numpy(audio)

        self._stft.process(self._hops_in, self._freqs_in)
        self._scm.process(self._freqs_in, self._masks, self._covs)
        self._phat.process(self._covs, self._covs_phat)
        self._gcc.process(self._covs_phat, self._tdoas)
        self._delaysum.process(self._tdoas, self._weights)
        self._beamformer.process(self._freqs_in, self._weights, self._freqs_out)
        self._istft.process(self._freqs_out, self._hops_out)

        return DelaySumPipelineResult(self._hops_out.to_numpy().copy())
