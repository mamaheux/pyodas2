import math

import pytest

from pyodas2.signals import Tdoas, Weights
from pyodas2.systems import DelaySum


def test_init():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 9

    testee = DelaySum(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    assert testee.num_sources == NUM_SOURCES
    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_SOURCES = 3
    NUM_CHANNELS = 4
    NUM_BINS = 9

    testee = DelaySum(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    with pytest.raises(ValueError, match='The number of channels of the tdoas must be 4.'):
        testee.process(Tdoas('', NUM_CHANNELS + 1, NUM_SOURCES),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='The number of sources of the tdoas must be 3.'):
        testee.process(Tdoas('', NUM_CHANNELS, NUM_SOURCES + 1),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='The number of sources of the weights must be 3.'):
        testee.process(Tdoas('', NUM_CHANNELS, NUM_SOURCES),
                       Weights('', NUM_SOURCES + 1, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='The number of channels of the weights must be 4.'):
        testee.process(Tdoas('', NUM_CHANNELS, NUM_SOURCES),
                       Weights('', NUM_SOURCES, NUM_CHANNELS + 1, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the weights must be 9.'):
        testee.process(Tdoas('', NUM_CHANNELS, NUM_SOURCES),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS + 1))


def test_process():
    NUM_SOURCES = 3
    NUM_CHANNELS = 4
    NUM_BINS = 9

    testee = DelaySum(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    tdoas = Tdoas('tdoas', NUM_CHANNELS, NUM_SOURCES)
    weights = Weights('Ws', NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    delays = [[-1.4927, -2.9854, -1.4927, -1.4927, +0.0000, +1.4927],
              [+1.4927, +0.0000, -1.4927, -1.4927, -2.9854, -1.4927],
              [+0.0000, +2.1107, +2.1107, +2.1107, +2.1107, +0.0000]]

    for s in range(tdoas.num_sources):
        for p in range(tdoas.num_pairs):
            tdoas[s, p].delay = delays[s][p]
            tdoas[s, p].amplitude = 1.0

    testee.process(tdoas, weights)

    weights = weights.to_numpy()
    for s in range(NUM_SOURCES):
        for c in range(NUM_CHANNELS):
            delay = delays[s][c] - delays[s][0]
            for b in range(NUM_BINS):
                target_real = (1.0 / NUM_CHANNELS) * math.cos(2.0 * math.pi * b * delay / ((NUM_BINS - 1) * 2))
                target_imag = (1.0 / NUM_CHANNELS) * math.sin(2.0 * math.pi * b * delay / ((NUM_BINS - 1) * 2))

                assert math.isclose(weights[s, c, b].real, target_real, abs_tol=1e-3)
                assert math.isclose(weights[s, c, b].imag, target_imag, abs_tol=1e-3)


def test_repr():
    testee = DelaySum(2, 4, 8)
    assert repr(testee) == '<pyodas2.systems.DelaySum (S=2, C=4, B=8)>'
