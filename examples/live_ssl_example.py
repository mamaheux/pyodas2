import threading
import time

import pyaudio
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from pyodas2.utils import Mics
from pyodas2.pipelines import SslPipeline

HOP_LENGTH = 128
RATE = 16000


lock = threading.Lock()
directions = np.zeros((0, 3))
stop_requested = False


def audio_thread_run():
    global directions

    mics = Mics(Mics.Hardware.RESPEAKER_USB_6)
    pipeline = SslPipeline(mics, sample_rate=RATE, hop_length=HOP_LENGTH)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=len(mics),
                    rate=RATE,
                    input=True)

    while not stop_requested:
        audio = np.frombuffer(stream.read(HOP_LENGTH), dtype=np.int32).reshape(-1, len(mics)).T
        result = pipeline.process(audio)

        with lock:
            directions = np.zeros((len(result.directions), 3))
            for i in range(len(result.directions)):
                directions[i, 0] = result.directions[i].coord.x
                directions[i, 1] = result.directions[i].coord.y
                directions[i, 2] = result.directions[i].coord.z
        time.sleep(0.1)


def main():
    audio_thread = threading.Thread(target=audio_thread_run)
    audio_thread.start()

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    def update(_):
        global directions
        with lock:
            new_directions = directions

        ax.clear()
        ax.scatter(new_directions[:, 0], new_directions[:, 1], new_directions[:, 2])
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

    _animation = FuncAnimation(fig, func=update, interval=100)

    try:
        plt.show()
    finally:
        global stop_requested
        stop_requested = True
        audio_thread.join()


if __name__ == '__main__':
    main()