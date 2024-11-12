import pytest

import math
import numpy as np

from pyodas2.systems import Istft, Window
from pyodas2.signals import Hops, Freqs


@pytest.mark.parametrize("num_bins", [8, 10])
def test_init_invalid_num_bins(num_bins):
    NUM_CHANNELS = 4

    with pytest.raises(ValueError):
        NUM_SAMPLES = 15
        NUM_SHIFTS = 4
        Istft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    with pytest.raises(ValueError):
        NUM_SAMPLES = 16
        NUM_SHIFTS = 17
        Istft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)


def test_init():
    NUM_CHANNELS = 4
    NUM_SAMPLES = 16
    NUM_SHIFTS = 8
    NUM_BINS = 9

    testee = Istft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_samples == NUM_SAMPLES
    assert testee.num_shifts == NUM_SHIFTS
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_CHANNELS = 2
    NUM_SAMPLES = 16
    NUM_SHIFTS = 4
    NUM_BINS = 9

    testee = Istft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    with pytest.raises(ValueError):
        testee.process(Freqs('Xs', NUM_CHANNELS + 1, NUM_BINS),
                       Hops('xs', NUM_CHANNELS, NUM_SHIFTS))

    with pytest.raises(ValueError):
        testee.process(Freqs('Xs', NUM_CHANNELS, NUM_BINS + 1),
                       Hops('xs', NUM_CHANNELS, NUM_SHIFTS))

    with pytest.raises(ValueError):
        testee.process(Freqs('Xs', NUM_CHANNELS, NUM_BINS),
                       Hops('xs', NUM_CHANNELS + 1, NUM_SHIFTS))

    with pytest.raises(ValueError):
        testee.process(Freqs('Xs', NUM_CHANNELS, NUM_BINS),
                       Hops('xs', NUM_CHANNELS, NUM_SHIFTS + 1))


def test_process():
    NUM_CHANNELS = 2
    NUM_SAMPLES = 16
    NUM_SHIFTS = 4
    NUM_BINS = 9

    testee = Istft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    freqs = Freqs('Xs', NUM_CHANNELS, NUM_BINS)
    hops = Hops('xs', NUM_CHANNELS, NUM_SHIFTS)

    freqs.load_numpy(np.array(
        [[+2.0 + 0.0j, -1.0 + 1.0j, +3.0 + 0.0j, +0.0 - 1.0j, -2.0 + 2.0j, +1.0 + 2.0j, +2.0 - 1.0j, -3.0 - 1.0j, +1.0 + 0.0j],
         [+1.0 + 0.0j, -2.0 + 1.0j, +2.0 + 0.0j, +1.0 - 1.0j, -2.0 + 2.0j, -2.0 + 2.0j, +1.0 - 1.0j, +3.0 - 1.0j, +2.0 + 0.0j]], dtype=np.complex64))
    testee.process(freqs, hops)

    expected_hops = np.array([[+0.000, +0.002, -0.007, +0.197], [+0.000, -0.030, +0.096, -0.121]], dtype=np.float32)
    assert np.allclose(hops.to_numpy(), expected_hops, atol=1e-3)

    freqs.load_numpy(np.array(
        [[+1.0 + 0.0j, +1.0 - 2.0j, +2.0 + 1.0j, +3.0 + 2.0j, -1.0 - 1.0j, -2.0 - 1.0j, +1.0 + 2.0j, +0.0 + 3.0j, +2.0 + 0.0j],
         [+3.0 + 0.0j, +2.0 - 3.0j, +1.0 + 3.0j, -1.0 - 1.0j, -1.0 - 2.0j, +2.0 + 2.0j, -1.0 + 2.0j, +0.0 - 1.0j, -1.0 + 0.0j]], dtype=np.complex64))
    testee.process(freqs, hops)

    expected_hops = np.array([[-0.725, -0.392, +1.090, -0.380], [-0.587, +0.125, +0.537, +0.616]], dtype=np.float32)
    assert np.allclose(hops.to_numpy(), expected_hops, atol=1e-3)
