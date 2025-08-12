import math

import pytest

from pyodas2.signals import Doas, Tdoas
from pyodas2.systems import Steering
from pyodas2.types import Xyz
from pyodas2.utils import Mic, Mics


def test_init_not_enough_mics():
    with pytest.raises(ValueError, match='Number of microphones must be at least 2.'):
        Steering(Mics([Mic(Xyz(0, 0, 0), Xyz(1, 0, 0), Mic.Pattern.OMNIDIRECTIONAL)]), 16000.0, 343.0, 3)


def test_init_invalid_sample_rate():
    Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 0.1, 343.0, 3)
    with pytest.raises(ValueError, match='Sample rate must be greater than 0.'):
        Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 0.0, 343.0, 3)


def test_init_invalid_sound_speed():
    Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 16000.0, 0.1, 3)
    with pytest.raises(ValueError, match='Sound speed must be greater than 0.'):
        Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 16000.0, 0.0, 3)


def test_init_not_enough_sources():
    Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 16000.0, 343.0, 1)
    with pytest.raises(ValueError, match='Number of sources must be at least 1.'):
        Steering(Mics(Mics.Hardware.RESPEAKER_USB_4), 16000.0, 343.0, 0)


def test_init():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_PAIRS = 6
    NUM_SOURCES = 3

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee = Steering(mics, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES)

    assert testee.num_channels == len(mics)
    assert testee.num_pairs == NUM_PAIRS
    assert testee.num_sources == NUM_SOURCES
    assert testee.mics == mics
    assert testee.sample_rate == SAMPLE_RATE
    assert testee.sound_speed == SOUND_SPEED


def test_process_invalid_inputs():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_SOURCES = 3

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee = Steering(mics, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES)

    with pytest.raises(
        ValueError, match='Number of directions in input DOAs must match the number of sources in the steering.'
    ):
        testee.process(Doas('doas', NUM_SOURCES + 1), Tdoas('tdoas', len(mics), NUM_SOURCES))

    with pytest.raises(
        ValueError, match='Number of channels in TDOAs must match the number of channels in the steering.'
    ):
        testee.process(Doas('doas', NUM_SOURCES), Tdoas('tdoas', len(mics) + 1, NUM_SOURCES))

    with pytest.raises(
        ValueError, match='Number of sources in TDOAs must match the number of sources in the steering.'
    ):
        testee.process(Doas('doas', NUM_SOURCES), Tdoas('tdoas', len(mics), NUM_SOURCES + 1))

    doas = Doas('doas', NUM_SOURCES)
    doas[0].coord = Xyz(-1.0, 0.0, 0.0)
    doas[1].coord = Xyz(0.0, 1.0, 0.0)
    doas[2].coord = Xyz(0.0, 1.0, 1.0)
    with pytest.raises(ValueError, match='All doas direction norms must be 1.'):
        testee.process(doas, Tdoas('tdoas', len(mics), NUM_SOURCES))


def test_process():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_PAIRS = 6
    NUM_SOURCES = 3

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee = Steering(mics, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES)

    doas = Doas('doas', NUM_SOURCES)
    tdoas = Tdoas('tdoas', len(mics), NUM_SOURCES)

    doas[0].coord = Xyz(-1.0, 0.0, 0.0)
    doas[0].energy = 0.1
    doas[1].coord = Xyz(0.0, -1.0, 0.0)
    doas[1].energy = 0.1
    doas[2].coord = Xyz(0.707, 0.707, 0)
    doas[2].energy = 0.1

    testee.process(doas, tdoas)

    expected_tdoas = [
        [-1.4927, -2.9854, -1.4927, -1.4927, +0.0000, +1.4927],
        [+1.4927, +0.0000, -1.4927, -1.4927, -2.9854, -1.4927],
        [+0.0000, +2.1107, +2.1107, +2.1107, +2.1107, +0.0000],
    ]

    for s in range(NUM_SOURCES):
        for p in range(NUM_PAIRS):
            assert math.isclose(tdoas[s, p].delay, expected_tdoas[s][p], abs_tol=1e-3)


def test_repr():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_SOURCES = 3

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee = Steering(mics, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES)
    assert repr(testee) == '<pyodas2.systems.Steering (C=4, S=3)>'
