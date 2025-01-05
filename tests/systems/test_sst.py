import math

import pytest

from pyodas2.signals import Doas, Dsf
from pyodas2.systems import Sst
from pyodas2.types import Xyz


def test_init():
    NUM_TRACKS = 3
    NUM_DIRECTIONS = 4
    NUM_PASTS = 40

    testee = Sst(NUM_TRACKS, NUM_DIRECTIONS, NUM_PASTS)

    assert testee.num_tracks == NUM_TRACKS
    assert testee.num_directions == NUM_DIRECTIONS
    assert math.isclose(testee.num_pasts, NUM_PASTS, abs_tol=1e-6)


def test_process_invalid_inputs():
    NUM_TRACKS = 3
    NUM_DIRECTIONS = 4
    NUM_PASTS = 40

    testee = Sst(NUM_TRACKS, NUM_DIRECTIONS, NUM_PASTS)

    with pytest.raises(ValueError, match='The number of directions of the input must be 4.'):
        testee.process(Dsf(''),
                       Doas('', NUM_DIRECTIONS + 1),
                       Doas('', NUM_TRACKS))

    with pytest.raises(ValueError, match='The number of directions of the output must be 3.'):
        testee.process(Dsf(''),
                       Doas('', NUM_DIRECTIONS),
                       Doas('', NUM_TRACKS + 1))


def test_process():
    NUM_TRACKS = 3
    NUM_DIRECTIONS = 4
    NUM_PASTS = 40

    testee = Sst(NUM_TRACKS, NUM_DIRECTIONS, NUM_PASTS)

    dsf = Dsf('')
    doas_src = Doas('', NUM_DIRECTIONS)
    doas_dst = Doas('', NUM_TRACKS)

    targets = [
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.707, 0.707, 0.0), 0.5),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.0, 1.0, 0.0), 0.1),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(-0.707, -0.707, 0.0), 0.1),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(-1.0, 0.0, 0.0), 0.05),
    ]

    noises = [
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.001, -0.002, 0.001), 0.01),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(-0.002, 0.001, -0.003), -0.01),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.015, -0.012, 0.004), 0.02),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(-0.012, 0.007, 0.013), 0.01),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.001, -0.012, 0.011), 0.03),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.020, 0.021, 0.008), -0.03),
        Doas.Dir(Doas.Src.POTENTIAL, Xyz(0.005, -0.005, 0.001), -0.02),
    ]

    index_noise = 0
    for _index_frame in range(20):
        for index_pot in range(NUM_DIRECTIONS):
            doas_src[index_pot] = targets[index_pot]
            doas_src[index_pot].coord = (doas_src[index_pot].coord + noises[index_noise].coord).unit()
            doas_src[index_pot].energy += noises[index_noise].energy

            index_noise += 1
            index_noise %= len(noises)

        testee.process(dsf, doas_src, doas_dst)

    assert doas_dst[0].type == Doas.Src.TRACKED
    assert (doas_dst[0].coord - targets[0].coord).mag() < 0.01

    assert doas_dst[1].type == Doas.Src.UNDEFINED
    assert doas_dst[2].type == Doas.Src.UNDEFINED


def test_repr():
    NUM_TRACKS = 3
    NUM_DIRECTION = 4
    NUM_PASTS = 40

    testee = Sst(NUM_TRACKS, NUM_DIRECTION, NUM_PASTS)
    assert repr(testee) == '<pyodas2.systems.Sst (T=3, D=4, P=40)>'
