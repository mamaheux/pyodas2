import pytest

import numpy as np

from pyodas2.systems import Stft, Window
from pyodas2.signals import Hops, Freqs


@pytest.mark.parametrize("num_bins", [8, 10])
def test_init_invalid_num_bins(num_bins):
    NUM_CHANNELS = 4

    with pytest.raises(ValueError):
        NUM_SAMPLES = 15
        NUM_SHIFTS = 4
        Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    with pytest.raises(ValueError):
        NUM_SAMPLES = 16
        NUM_SHIFTS = 17
        Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)


def test_init():
    NUM_CHANNELS = 4
    NUM_SAMPLES = 16
    NUM_SHIFTS = 8
    NUM_BINS = 9

    testee = Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_samples == NUM_SAMPLES
    assert testee.num_shifts == NUM_SHIFTS
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_CHANNELS = 2
    NUM_SAMPLES = 16
    NUM_SHIFTS = 4
    NUM_BINS = 9

    testee = Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    with pytest.raises(ValueError):
        testee.process(Hops('xs', NUM_CHANNELS + 1, NUM_SHIFTS),
                       Freqs('Xs', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Hops('xs', NUM_CHANNELS, NUM_SHIFTS + 1),
                       Freqs('Xs', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Hops('xs', NUM_CHANNELS, NUM_SHIFTS),
                       Freqs('Xs', NUM_CHANNELS + 1, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Hops('xs', NUM_CHANNELS, NUM_SHIFTS),
                       Freqs('Xs', NUM_CHANNELS, NUM_BINS + 1))


def test_process():
    NUM_CHANNELS = 2
    NUM_SAMPLES = 16
    NUM_SHIFTS = 4
    NUM_BINS = 9

    testee = Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)

    hops = Hops('xs', NUM_CHANNELS, NUM_SHIFTS)
    freqs = Freqs('Xs', NUM_CHANNELS, NUM_BINS)

    hops.load_numpy(np.array([[+1.0, -2.0, +2.0, +1.0], [+2.0, +3.0, +0.0, -1.0]], dtype=np.float32))
    testee.process(hops, freqs)

    expected_freqs = np.array(
        [[+0.101 + 0.000j, -0.065 + 0.101j, -0.112 - 0.148j, +0.245 - 0.158j, +0.259 + 0.331j, -0.367 + 0.411j, -0.579 - 0.320j, +0.188 - 0.712j, +0.763 + 0.000j],
         [+1.187 + 0.000j, +0.190 + 1.150j, -1.042 + 0.351j, -0.459 - 0.881j, +0.691 - 0.496j, +0.459 + 0.501j, -0.340 + 0.351j, -0.190 - 0.232j, +0.195 + 0.000j]], dtype=np.complex64)
    assert np.allclose(freqs.to_numpy(), expected_freqs, atol=1e-3)

    hops.load_numpy(np.array([[-1.0, -3.0, +0.0, -3.0], [-3.0, -1.0, +1.0, -1.0]], dtype=np.float32))
    testee.process(hops, freqs)

    expected_freqs = np.array(
        [[+0.391 + 0.000j, -0.780 + 0.075j, +0.016 - 0.962j, +1.733 - 0.287j, -0.856 + 2.858j, -1.589 - 3.099j, +2.653 + 2.038j, -3.320 - 1.356j, +3.897 + 0.000j],
         [+2.981 + 0.000j, -4.307 - 0.631j, +5.441 - 1.602j, -3.405 + 3.849j, +0.898 - 3.100j, -0.613 + 1.715j, +0.588 - 1.688j, +0.411 + 1.381j, -1.011 + 0.000j]], dtype=np.complex64)
    assert np.allclose(freqs.to_numpy(), expected_freqs, atol=1e-3)


def test_repr():
    NUM_CHANNELS = 2
    NUM_SAMPLES = 16
    NUM_SHIFTS = 4

    testee = Stft(NUM_CHANNELS, NUM_SAMPLES, NUM_SHIFTS, Window.HANN)
    assert repr(testee) == '<pyodas2.systems.Stft (C=2, Sa=16, Sh=4, B=9)>'
