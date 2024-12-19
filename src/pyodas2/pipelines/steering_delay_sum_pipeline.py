from dataclasses import dataclass

import numpy as np

from pyodas2.utils import Mics, Points
from pyodas2.signals import Hops, Freqs, Doas, Tdoas, Weights
from pyodas2.systems import Stft, Window, Steering, DelaySum, Beamformer, Istft
from pyodas2.types import Xyz


@dataclass
class SteeringDelaySumPipelineResult:
    """
    This is a class representing the results of the delay and sum beamforming
    """
    audio: np.ndarray


class SteeringDelaySumPipeline:
    """
    This is a class performing delay and sum beamforming at given directions.
    """

    def __init__(self,
                 mics: Mics,
                 sample_rate: float = 16000,
                 hop_length: int = 128,
                 num_sources: int = 1,
                 n_fft: int = 512,
                 fft_window: Window = Window.HANN,
                 sound_speed: float = 343.0,):
        """
        Create a new steering delay and sum pipeline.

        :param mics: The microphone positions and directions of the microphone array
        :param sample_rate: The sample rate of the sound.
        :param hop_length:
        :param num_sources: The number of samples in each processed audio frame, also named num_shifts.
        :param n_fft: The size of the FFT for the STFT. It must be a power of 2.
        :param fft_window: The window type to compute the FFT for the STFT.
        :param sound_speed: The speed of sound in m/s.
        """

        self._num_channels = len(mics)
        self._num_bins = n_fft // 2 + 1

        self._hops_in = Hops("xs", self._num_channels, hop_length)
        self._freqs_in = Freqs("Xs", self._num_channels, self._num_bins)
        self._doas = Doas("doas", num_sources)
        self._tdoas = Tdoas("tdoas", self._num_channels, num_sources)
        self._weights = Weights("Ws", num_sources, self._num_channels, self._num_bins)
        self._freqs_out = Freqs("Ys", num_sources, self._num_bins)
        self._hops_out = Hops("ys", num_sources, hop_length)

        self._stft = Stft(self._num_channels, n_fft, hop_length, fft_window)
        self._steering = Steering(mics, sample_rate, sound_speed, num_sources)
        self._delaysum = DelaySum(num_sources, self._num_channels, self._num_bins)
        self._beamformer = Beamformer(num_sources, self._num_channels, self._num_bins)
        self._istft = Istft(num_sources, n_fft, hop_length, fft_window)

    def process(self, audio: np.ndarray) -> SteeringDelaySumPipelineResult:
        """
        Process the current audio frame

        :param audio: The audio data having the shape (len(mics), hop_length)
        :return: The result for the current audio frame
        """
        self._hops_in.load_numpy(audio)

        self._stft.process(self._hops_in, self._freqs_in)
        self._delaysum.process(self._tdoas, self._weights)
        self._beamformer.process(self._freqs_in, self._weights, self._freqs_out)
        self._istft.process(self._freqs_out, self._hops_out)

        return SteeringDelaySumPipelineResult(self._hops_out.to_numpy().copy())

    def set_directions(self, directions: [Xyz]):
        """
        Update the directions to listen.

        :param directions: The list of directions to listen. The length must be equal to the number of source.
        :return: None
        """
        if len(directions) != len(self._doas):
            raise ValueError(f'Expected {len(self._doas)} directions')

        for i in range(len(directions)):
            self._doas[i].type = Doas.Src.TARGET
            self._doas[i].coord = directions[i].unit()
            self._doas[i].energy = 1.0

        self._steering.process(self._doas, self._tdoas)