from typing import List, Dict
from dataclasses import dataclass

import numpy as np

from pyodas2.utils import Mics, Points
from pyodas2.signals import Hops, Freqs, Masks, Covs, Tdoas, Doas, Dsf, Weights
from pyodas2.systems import Stft, Window, Scm, Phat, Gcc, Ssl, Sst, Steering, DelaySum, Beamformer, Istft


@dataclass
class SstDelaySumPipelineResult:
    """
    This is a class representing the results of the sound source tracking and delay and sum on the tracked directions.
    """
    potential_directions: List[Doas.Dir]
    tracked_directions_by_index: Dict[int, Doas.Dir]
    audio: np.ndarray


class SstDelaySumPipeline:
    """
    This is a class performing sound source tracking and delay and sum on the tracked directions.
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
                 sst_num_pasts: int = 40):
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
        :param sst_num_pasts: TODO
        """

        self._num_bins = n_fft // 2 + 1
        self._num_channels = len(mics)
        self._points = Points(ssl_geometry)

        self._hops_in = Hops("xs", self._num_channels, hop_length)
        self._freqs_in = Freqs("Xs", self._num_channels, self._num_bins)
        self._masks = Masks("Ms", self._num_channels, self._num_bins)
        self._covs = Covs("XXs", self._num_channels, self._num_bins)
        self._covs_phat = Covs("XXps", self._num_channels, self._num_bins)
        self._tdoas = Tdoas("tdoas", self._num_channels, num_sources)
        self._doas_potential = Doas("doas_potential", num_directions)
        self._dsf = Dsf("dsf")
        self._doas_tracked = Doas("doas_tracked", num_tracks)
        self._tdoas_tracked = Tdoas("tdoas_tracked", self._num_channels, num_tracks)
        self._weights = Weights("Ws", num_tracks, self._num_channels, self._num_bins)
        self._freqs_out = Freqs("Ys", num_tracks, self._num_bins)
        self._hops_out = Hops("ys", num_tracks, hop_length)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._scm = Scm(self._num_channels, self._num_bins, scm_alpha)
        self._phat = Phat(self._num_channels, self._num_bins)
        self._gcc = Gcc(num_sources, self._num_channels, self._num_bins)
        self._ssl = Ssl(mics, self._points, sample_rate, sound_speed, num_sources, num_directions)
        self._sst = Sst(num_tracks, num_directions, sst_num_pasts)
        self._steering = Steering(mics, sample_rate, sound_speed, num_tracks)
        self._delaysum = DelaySum(num_tracks, self._num_channels, self._num_bins)
        self._beamformer = Beamformer(num_tracks, self._num_channels, self._num_bins)
        self._istft = Istft(num_tracks, n_fft, hop_length, fft_window)

        self._masks.set_ones()

    def process(self, audio: np.ndarray) -> SstDelaySumPipelineResult:
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
        self._ssl.process(self._tdoas, self._doas_potential)
        self._sst.process(self._dsf, self._doas_potential, self._doas_tracked)

        self._steering.process(self._doas_tracked, self._tdoas_tracked)
        self._delaysum.process(self._tdoas_tracked, self._weights)
        self._beamformer.process(self._freqs_in, self._weights, self._freqs_out)
        self._istft.process(self._freqs_out, self._hops_out)

        output_audio = self._hops_out.to_numpy().copy()
        for i, d in enumerate(self._doas_tracked):
            if d.type != Doas.Src.TRACKED:
                output_audio[i, :] = 0

        return SstDelaySumPipelineResult(
            [d.copy() for d in self._doas_potential if d.type == Doas.Src.POTENTIAL],
            {i: d.copy() for i, d in enumerate(self._doas_tracked) if d.type == Doas.Src.TRACKED},
            output_audio
        )