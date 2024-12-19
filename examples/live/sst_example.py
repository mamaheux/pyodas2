"""
This is an example to illustrate how to perform sound source tracking using a live audio stream.
"""

import threading

import alsaaudio
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from pyodas2.utils import Mics
from pyodas2.pipelines import SstPipeline

HOP_LENGTH = 128
RATE = 16000


lock = threading.Lock()
potential_directions = np.zeros((0, 3))
tracked_directions = np.zeros((0, 3))
stop_requested = False


def audio_thread_run():
    global potential_directions
    global tracked_directions

    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = SstPipeline(mics, sample_rate=RATE, hop_length=HOP_LENGTH)

    pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                        channels=len(mics), rate=RATE, format=alsaaudio.PCM_FORMAT_S32_LE,
                        periodsize=HOP_LENGTH, device='hw:CARD=SC16,DEV=0')

    while not stop_requested:
        l, data = pcm.read()
        if l < 0:
            continue

        audio = np.frombuffer(data, dtype=np.int32).reshape(-1, len(mics)).T
        result = pipeline.process(audio)

        with lock:
            potential_directions = np.zeros((len(result.potential_directions), 3))
            for i, d in enumerate(result.potential_directions):
                potential_directions[i, 0] = d.coord.x
                potential_directions[i, 1] = d.coord.y
                potential_directions[i, 2] = d.coord.z

            tracked_directions = np.zeros((len(result.tracked_directions_by_index), 3))
            for i, d in enumerate(result.tracked_directions_by_index.values()):
                tracked_directions[i, 0] = d.coord.x
                tracked_directions[i, 1] = d.coord.y
                tracked_directions[i, 2] = d.coord.z


def main():
    audio_thread = threading.Thread(target=audio_thread_run)
    audio_thread.start()

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    def update(_):
        global potential_directions
        global tracked_directions

        with lock:
            new_potential_directions = potential_directions
            new_tracked_directions = tracked_directions

        ax.clear()
        ax.scatter(new_potential_directions[:, 0], new_potential_directions[:, 1], new_potential_directions[:, 2],
                   color='blue', label='Potential')
        ax.scatter(new_tracked_directions[:, 0], new_tracked_directions[:, 1], new_tracked_directions[:, 2],
                   color='red', label='Tracked')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()

    _animation = FuncAnimation(fig, func=update, interval=100)

    try:
        plt.show()
    finally:
        global stop_requested
        stop_requested = True
        audio_thread.join()


if __name__ == '__main__':
    main()
