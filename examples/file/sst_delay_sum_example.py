"""
This is an example to illustrate how to perform sound source tracking and delay and sum beamforming using a file.
"""

import os
import wave

import numpy as np

from pyodas2.utils import Mics
from pyodas2.pipelines import SstDelaySumPipeline, SstDelaySumPipelineResult


INPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix.wav')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.wav')

HOP_LENGTH = 128
NUM_SOURCES = 1
NUM_TRACKS = 3

OUTPUT_SAMPLE_WIDTH=2


def main():
    with wave.open(INPUT_PATH, 'rb') as wave_reader, wave.open(OUTPUT_PATH, 'wb') as wave_writer:
        wave_writer.setnchannels(NUM_TRACKS)
        wave_writer.setsampwidth(OUTPUT_SAMPLE_WIDTH)
        wave_writer.setframerate(wave_reader.getframerate())

        mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
        pipeline = SstDelaySumPipeline(mics, hop_length=HOP_LENGTH, num_sources=NUM_SOURCES, num_tracks=NUM_TRACKS)

        data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()
        while True:
            data = wave_reader.readframes(HOP_LENGTH)
            if len(data) != data_size:
                break

            audio = bytes_to_numpy(data, wave_reader.getnchannels(), wave_reader.getsampwidth())
            result = pipeline.process(audio)

            display_result(result)
            wave_writer.writeframes(numpy_to_bytes(result.audio))


def bytes_to_numpy(data: bytes, nchannels: int, sample_width: int) -> np.ndarray:
    if sample_width == 2:
        return np.frombuffer(data, dtype=np.int16).reshape(-1, nchannels).T
    else:
        raise ValueError('Not supported sample width.')


def numpy_to_bytes(audio: np.ndarray[np.float32]) -> bytes:
    if OUTPUT_SAMPLE_WIDTH == 2:
        return (audio * np.iinfo(np.int16).max).astype(np.int16).T.tobytes()
    else:
        raise ValueError('Not supported sample width.')


def display_result(result: SstDelaySumPipelineResult):
    print('Potential directions')
    for d in result.potential_directions:
        print('\tenergy:', d.energy, '\tdirection:', d.coord)

    print('Tracked directions')
    for i, d in result.tracked_directions_by_index.items():
        print('\t', i, '\tenergy:', d.energy, '\tdirection:', d.coord)

    print()


if __name__ == '__main__':
    main()
