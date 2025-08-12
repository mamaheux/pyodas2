import math

import numpy as np
import pytest

from pyodas2.signals import Covs, Tdoas
from pyodas2.systems import Gcc


def test_init_not_enough_sources():
    Gcc(1, 4, 9)
    with pytest.raises(ValueError, match='Number of sources must be at least 1.'):
        Gcc(0, 4, 9)


def test_init_not_enough_channels():
    Gcc(2, 2, 9)
    with pytest.raises(ValueError, match='Number of channels must be at least 2.'):
        Gcc(2, 1, 9)


def test_init_invalid_bins():
    Gcc(2, 4, 9)
    with pytest.raises(
        ValueError, match='Number of bins converted to number of samples must be at least 2 and a power of 2.'
    ):
        Gcc(2, 4, 8)


def test_init():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 9

    testee = Gcc(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    assert testee.num_sources == NUM_SOURCES
    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_pairs == 6
    assert testee.num_bins == NUM_BINS
    assert testee.num_samples == 16
    assert testee.interpolation_factor == 2


def test_process_invalid_inputs():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 9

    testee = Gcc(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    with pytest.raises(ValueError, match='Number of channels in covs must match the number of channels in the GCC.'):
        testee.process(Covs('', NUM_CHANNELS + 1, NUM_BINS), Tdoas('', NUM_CHANNELS, NUM_SOURCES))

    with pytest.raises(ValueError, match='Number of bins in covs must match the number of bins in the GCC.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS + 1), Tdoas('', NUM_CHANNELS, NUM_SOURCES))

    with pytest.raises(ValueError, match='Number of channels in TDOAs must match the number of channels in the GCC.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS), Tdoas('', NUM_CHANNELS + 1, NUM_SOURCES))

    with pytest.raises(ValueError, match='Number of sources in TDOAs must match the number of sources in the GCC.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS), Tdoas('', NUM_CHANNELS, NUM_SOURCES + 1))


def test_process():
    NUM_SOURCES = 1
    NUM_CHANNELS = 3
    NUM_BINS = 257
    NUM_BINS_CROPPED = 100

    DELAYS = [2.3, -15.25, 6.5]
    AMPLITUDES = [0.39, 0.39, 0.39]

    testee = Gcc(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)
    covs = Covs('XXs', NUM_CHANNELS, NUM_BINS)
    tdoas = Tdoas('tdoas', NUM_CHANNELS, NUM_SOURCES)

    xcorrs = np.zeros((NUM_CHANNELS, NUM_BINS), dtype=np.complex64)
    for p in range(testee.num_pairs):
        for b in range(NUM_BINS_CROPPED):
            omega = 2.0 * math.pi * b / ((NUM_BINS - 1) * 2)
            xcorrs[p, b] = math.cos(-omega * DELAYS[p]) + 1j * math.sin(-omega * DELAYS[p])
    covs.xcorrs_load_numpy(xcorrs)

    testee.process(covs, tdoas)

    for p in range(testee.num_pairs):
        assert math.isclose(tdoas[0, p].delay, DELAYS[p], abs_tol=0.2)
        assert math.isclose(tdoas[0, p].amplitude, AMPLITUDES[p], abs_tol=0.025)


def test_repr():
    NUM_SOURCES = 1
    NUM_CHANNELS = 3
    NUM_BINS = 257
    testee = Gcc(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)
    assert repr(testee) == '<pyodas2.systems.Gcc (S=1, C=3, B=257)>'
