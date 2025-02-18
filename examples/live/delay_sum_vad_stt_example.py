"""
This is an example to illustrate how to perform sound source tracking, delay-and-sum beamforming using a live audio stream.
"""

# TODO use MVDR instead of delay-and-sum beamforming

import queue
import threading

import alsaaudio
import numpy as np
import torch
import whisper

from pyodas2.pcm import interleaved_pcm_to_numpy
from pyodas2.pipelines import DelaySumPipeline
from pyodas2.utils import Mics

HOP_LENGTH = 512
N_FFT = 1024
RATE = 16000
NUM_SOURCES = 1
PERIODS = 10

VOICE_PROBABILITY_THRESHOLD = 0.5
PREBUFFERING_DURATION_S = 0.5
PREBUFFERING_DURATION_HOP = int(PREBUFFERING_DURATION_S * RATE / HOP_LENGTH)
SILENCE_DURATION_S = 1.0
SILENCE_DURATION_HOP = int(SILENCE_DURATION_S * RATE / HOP_LENGTH)
LANGUAGE = 'en'


def audio_thread_run(stop_event: threading.Event, stt_queue: queue.Queue):
    vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')

    mics = Mics(Mics.Hardware.SC16_DEMO_ARRAY)
    pipeline = DelaySumPipeline(
        mics,
        hop_length=HOP_LENGTH,
        n_fft=N_FFT,
        num_sources=NUM_SOURCES,
    )

    input_pcm = alsaaudio.PCM(
        alsaaudio.PCM_CAPTURE,
        alsaaudio.PCM_NORMAL,
        channels=len(mics),
        rate=RATE,
        format=alsaaudio.PCM_FORMAT_S32_LE,
        periodsize=HOP_LENGTH,
        periods=PERIODS,
        device='hw:CARD=SC16,DEV=0',
    )

    print('Audio processing started')

    silence_hop = 0
    frames = [np.zeros(HOP_LENGTH, dtype=np.float32) for _ in range(PREBUFFERING_DURATION_HOP)]
    while not stop_event.is_set():
        _length, input_data = input_pcm.read()

        # The dtype must match the input_pcm alsa format.
        input_audio = interleaved_pcm_to_numpy(input_data, len(mics), dtype=np.int32)
        result = pipeline.process(input_audio)
        frames.append(result.audio[0])

        voice_probability = vad_model(torch.from_numpy(result.audio[0]), RATE).item()

        if silence_hop <= 0 and voice_probability < VOICE_PROBABILITY_THRESHOLD:
            if (len(frames) - 1) > PREBUFFERING_DURATION_HOP:
                stt_queue.put(np.concatenate(frames))
            frames = frames[-PREBUFFERING_DURATION_HOP:]
        elif voice_probability < VOICE_PROBABILITY_THRESHOLD:
            silence_hop -= 1
        else:
            silence_hop = SILENCE_DURATION_HOP


def main():
    whisper_model = whisper.load_model('turbo')
    stt_queue = queue.Queue()

    stop_event = threading.Event()
    audio_thread = threading.Thread(target=audio_thread_run, args=[stop_event, stt_queue])
    audio_thread.start()

    try:
        while True:
            voice_sequence = stt_queue.get()
            result = whisper_model.transcribe(voice_sequence, language=LANGUAGE)
            print(result["text"])
    finally:
        stop_event.set()
        audio_thread.join()


if __name__ == '__main__':
    main()
