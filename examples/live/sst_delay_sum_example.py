"""
This is an example to illustrate how to perform sound source tracking and delay and sum beamforming using a live audio stream.
"""

import alsaaudio
import numpy as np

from pyodas2.utils import Mics
from pyodas2.pipelines import SstDelaySumPipeline, SstDelaySumPipelineResult

HOP_LENGTH = 128
RATE = 16000
NUM_SOURCES = 1
PERIODS = 10

def main():
    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = SstDelaySumPipeline(mics, hop_length=HOP_LENGTH, num_sources=NUM_SOURCES)

    input_pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                              channels=len(mics), rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                              periodsize=HOP_LENGTH, periods=PERIODS, device='hw:CARD=SC16,DEV=0')
    output_pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL,
                               channels=NUM_SOURCES, rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                               periodsize=HOP_LENGTH, periods=PERIODS, device='default')

    # Buffer the output PCM
    for _ in range(PERIODS):
        output_pcm.write(np.zeros(NUM_SOURCES * HOP_LENGTH, dtype=np.int32).tobytes())

    while True:
        l, input_data = input_pcm.read()

        input_audio = np.frombuffer(input_data, dtype=np.int32).reshape(-1, len(mics)).T
        result = pipeline.process(input_audio)


        most_energy_tracked_audio = get_most_energy_tracked_audio(result)
        output_data = (most_energy_tracked_audio * np.iinfo(np.int32).max).astype(np.int32).T.tobytes()
        output_pcm.write(output_data)


def get_most_energy_tracked_audio(result: SstDelaySumPipelineResult) -> np.ndarray:
    if len(result.tracked_directions_by_index.items()) == 0:
        return result.audio[0]

    i, _ = max(result.tracked_directions_by_index.items(), key=lambda x: x[1].energy)
    return result.audio[i]


if __name__ == '__main__':
    main()
