from typing import List, Dict
from dataclasses import dataclass

import numpy as np

from pyodas2.utils import Mics, Points
from pyodas2.signals import Hops, Freqs, Masks, Covs, Tdoas, Doas
from pyodas2.systems import Stft, Window, Scm, Phat, Gcc, Ssl, Sst


@dataclass
class SstPipelineResult:
    """
    This is a class representing the results of the sound source tracking
    """
    potential_directions: List[Doas.Dir]
    tracked_directions_by_index: Dict[int, Doas.Dir]


class SstPipeline:
    """
    This is a class performing sound source tracking.


                                 Ms (all 1's)
                                      |
                                      *
    +----+   xs   +------+   Xs   +-----+   XXs   +------+   XXps   +---------+  tdoas   +-----+  doas   +-----+  doas   +-----+
    | In | -----* | STFT | -----* | SCM | ------* | PHAT | -------* | GCC/FCC | -------* | SSL | ------* | SST | ------* | Out |
    +----+        +------+        +-----+         +------+          +---------+          +-----+         +-----+         +-----+
    """
    def __init__(self,
                 mics: Mics,
                 sample_rate: float = 16000,
                 hop_length: int = 128,
                 num_sources: int = 1,
                 num_directions: int = 2,
                 num_tracks: int = 3,
                 n_fft: int = 512,
                 fft_window: Window = Window.HANN,
                 sound_speed: float = 343.0,
                 ssl_geometry: Points.Geometry = Points.Geometry.HALFSPHERE,
                 scm_alpha: float = 0.5,
                 sst_delta_time: float = None,
                 sst_energy_threshold: float = 0.5):
        """
        Create a new sound source tracking pipeline.

        :param mics: The microphone positions and directions of the microphone array
        :param sample_rate: The sample rate of the sound
        :param hop_length: The number of samples in each processed audio frame, also named num_shifts.
        :param num_sources: The number of audio source
        :param num_directions: TODO num_directions vs num_sources vs num_tracks
        :param num_tracks: TODO num_directions vs num_sources vs num_tracks
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param sound_speed: The speed of sound in m/s.
        :param ssl_geometry: The geometry to perform the sound source localisation
        :param scm_alpha: TODO
        :param sst_delta_time: TODO
        :param sst_energy_threshold: TODO
        """

        if sst_delta_time is None:
            sst_delta_time = hop_length / sample_rate

        self._num_bins = n_fft // 2 + 1
        self._num_channels = len(mics)
        self._points = Points(ssl_geometry)

        self._hops = Hops("xs", self._num_channels, hop_length)
        self._freqs = Freqs("Xs", self._num_channels, self._num_bins)
        self._masks = Masks("Ms", self._num_channels, self._num_bins)
        self._covs = Covs("XXs", self._num_channels, self._num_bins)
        self._covs_phat = Covs("XXps", self._num_channels, self._num_bins)
        self._tdoas = Tdoas("tdoas", self._num_channels, num_sources)
        self._doas_potential = Doas("doas_potential", num_directions)
        self._doas_tracked = Doas("doas_tracked", num_tracks)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)
        self._phat = Phat(self._num_channels, self._num_bins)
        self._gcc = Gcc(num_sources, self._num_channels, self._num_bins)
        self._ssl = Ssl(mics, self._points, sample_rate, sound_speed, num_sources, num_directions)
        self._sst = Sst(num_tracks, num_directions, sst_delta_time, sst_energy_threshold)

        self._masks.set_ones()

    def process(self, audio: np.ndarray) -> SstPipelineResult:
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
        self._ssl.process(self._tdoas, self._doas_potential)
        self._sst.process(self._doas_potential, self._doas_tracked)

        return SstPipelineResult([d.copy() for d in self._doas_potential if d.type == Doas.Src.POTENTIAL],
                                 {i: d.copy() for i, d in enumerate(self._doas_tracked) if d.type == Doas.Src.TRACKED})
