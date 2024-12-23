"""
This is an example to illustrate how to perform sound source localization using a file.
"""

import os
import wave

from pyodas2.utils import Mics
from pyodas2.pipelines import SslPipeline, SslPipelineResult
from pyodas2.pcm import interleaved_pcm_to_numpy


AUDIO_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio', 'mix.wav')
HOP_LENGTH = 128


def main():
    with wave.open(AUDIO_PATH, 'rb') as wave_reader:
        mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
        pipeline = SslPipeline(mics, sample_rate=wave_reader.getframerate(), hop_length=HOP_LENGTH)

        data_size = HOP_LENGTH * wave_reader.getnchannels() * wave_reader.getsampwidth()
        while True:
            data = wave_reader.readframes(HOP_LENGTH)
            if len(data) != data_size:
                break

            audio = interleaved_pcm_to_numpy(data, wave_reader.getnchannels(), sample_width=wave_reader.getsampwidth())
            result = pipeline.process(audio)
            display_result(result)


def display_result(result: SslPipelineResult):
    for d in result.directions:
        print('energy:', d.energy, '\tdirection:', d.coord)
    print()

if __name__ == '__main__':
    main()
