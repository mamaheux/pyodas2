"""
This is an example to illustrate how to perform sound source tracking.
"""

import os
import wave

import numpy as np

from pyodas2.utils import Mics
from pyodas2.pipelines import SstPipeline, SstPipelineResult


AUDIO_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix.wav')
HOP_LENGTH = 128


def main():
    with wave.open(AUDIO_PATH, 'rb') as wave_reader:
        mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
        pipeline = SstPipeline(mics, sample_rate=wave_reader.getframerate(), hop_length=HOP_LENGTH)

        data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()
        while True:
            data = wave_reader.readframes(HOP_LENGTH)
            if len(data) != data_size:
                break

            audio = bytes_to_numpy(data, wave_reader.getnchannels(), wave_reader.getsampwidth())
            result = pipeline.process(audio)
            display_result(result)


def bytes_to_numpy(data: bytes, nchannels: int, sample_width: int) -> np.ndarray:
    if sample_width == 2:
        return np.frombuffer(data, dtype=np.int16).reshape(-1, nchannels).T
    else:
        raise ValueError('Not supported sample width.')


def display_result(result: SstPipelineResult):
    print('Potential directions')
    for d in result.potential_directions:
        print('\tenergy:', d.energy, '\tdirection:', d.coord)

    print('Tracked directions')
    for i, d in result.tracked_directions_by_index.items():
        print('\t', i, '\tenergy:', d.energy, '\tdirection:', d.coord)

    print()

if __name__ == '__main__':
    main()
