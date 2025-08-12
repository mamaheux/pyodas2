import math

import pytest

from pyodas2.signals import Doas, Tdoas
from pyodas2.systems import Ssl, Steering
from pyodas2.types import Xyz
from pyodas2.utils import Mic, Mics, Points


def test_init_not_enough_mics():
    with pytest.raises(ValueError, match='Number of microphones must be at least 2.'):
        Ssl(
            Mics([Mic(Xyz(0, 0, 0), Xyz(1, 0, 0), Mic.Pattern.OMNIDIRECTIONAL)]),
            Points(Points.Geometry.HALFSPHERE, 2562),
            16000.0,
            343.0,
            4,
            2,
        )


def test_init_not_enough_points():
    with pytest.raises(ValueError, match='Number of points must be at least 1.'):
        Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 0), 16000.0, 343.0, 4, 2)


def test_init_invalid_sample_rate():
    Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 0.1, 343.0, 4, 2)
    with pytest.raises(ValueError, match='Sample rate must be greater than 0.'):
        Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 0.0, 343.0, 4, 2)


def test_init_invalid_sound_speed():
    Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 0.1, 4, 2)
    with pytest.raises(ValueError, match='Sound speed must be greater than 0.'):
        Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 0.0, 4, 2)


def test_init_not_enough_sources():
    Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 343.0, 1, 2)
    with pytest.raises(ValueError, match='Number of sources must be at least 1.'):
        Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 343.0, 0, 2)


def test_init_not_enough_directions():
    Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 343.0, 4, 1)
    with pytest.raises(ValueError, match='Number of directions must be at least 1.'):
        Ssl(Mics(Mics.Hardware.RESPEAKER_USB_4), Points(Points.Geometry.HALFSPHERE, 2562), 16000.0, 343.0, 4, 0)


def test_init():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_PAIRS = 6
    NUM_SOURCES = 4
    NUM_DIRECTIONS = 2

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    points = Points(Points.Geometry.HALFSPHERE, 2562)
    testee = Ssl(mics, points, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES, NUM_DIRECTIONS)

    assert testee.num_channels == len(mics)
    assert testee.num_pairs == NUM_PAIRS
    assert testee.num_sources == NUM_SOURCES
    assert testee.num_directions == NUM_DIRECTIONS
    assert testee.num_points == len(points)
    assert testee.sample_rate == SAMPLE_RATE
    assert testee.sound_speed == SOUND_SPEED
    assert testee.mics == mics
    assert testee.points == points


def test_process_invalid_inputs():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_SOURCES = 4
    NUM_DIRECTIONS = 2

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    points = Points(Points.Geometry.HALFSPHERE, 2562)
    testee = Ssl(mics, points, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES, NUM_DIRECTIONS)

    with pytest.raises(ValueError, match='Number of channels in TDOAs must match the number of channels in the ssl.'):
        testee.process(Tdoas('tdoas', len(mics) + 1, NUM_SOURCES), Doas('doas', NUM_DIRECTIONS))

    with pytest.raises(ValueError, match='Number of sources in TDOAs must match the number of sources in the ssl.'):
        testee.process(Tdoas('tdoas', len(mics), NUM_SOURCES + 1), Doas('doas', NUM_DIRECTIONS))

    with pytest.raises(
        ValueError, match='Number of directions in DOAs must match the number of directions in the ssl.'
    ):
        testee.process(Tdoas('tdoas', len(mics), NUM_SOURCES), Doas('doas', NUM_DIRECTIONS + 1))


def test_process():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_SOURCES = 4
    NUM_DIRECTIONS = 2

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    points = Points(Points.Geometry.HALFSPHERE, 2562)
    testee = Ssl(mics, points, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES, NUM_DIRECTIONS)
    steering = Steering(mics, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES)

    tdoas = Tdoas('tdoas', len(mics), NUM_SOURCES)
    doas_src = Doas('doas_src', NUM_SOURCES)
    doas_dst = Doas('doas_dst', NUM_DIRECTIONS)

    doas_src[0].coord = Xyz(0.0, 1.0, 0.0)
    doas_src[0].energy = 0.25
    doas_src[1].coord = Xyz(0.707, 0.707, 0)
    doas_src[1].energy = 0.1
    doas_src[2].coord = Xyz(0.5773, 0.5773, 0.5773)
    doas_src[2].energy = 0.05
    doas_src[3].coord = Xyz(1.0, 0.0, 0.0)
    doas_src[3].energy = 0.5

    steering.process(doas_src, tdoas)
    testee.process(tdoas, doas_dst)

    assert math.isclose(doas_dst[0].coord.x, 1.0, abs_tol=0.1)
    assert math.isclose(doas_dst[0].coord.y, 0.0, abs_tol=0.1)
    assert math.isclose(doas_dst[0].coord.z, 0.0, abs_tol=0.1)

    assert math.isclose(doas_dst[1].coord.x, 0.0, abs_tol=0.1)
    assert math.isclose(doas_dst[1].coord.y, 1.0, abs_tol=0.1)
    assert math.isclose(doas_dst[1].coord.z, 0.0, abs_tol=0.1)


def test_repr():
    SAMPLE_RATE = 16000.0
    SOUND_SPEED = 343.0
    NUM_SOURCES = 4
    NUM_DIRECTIONS = 2

    mics = Mics(Mics.Hardware.RESPEAKER_USB_4)
    points = Points(Points.Geometry.HALFSPHERE, 2562)
    testee = Ssl(mics, points, SAMPLE_RATE, SOUND_SPEED, NUM_SOURCES, NUM_DIRECTIONS)
    assert repr(testee) == '<pyodas2.systems.Ssl (S=4, D=2)>'
