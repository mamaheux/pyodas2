import numpy as np
import pytest

from pyodas2.signals import Freqs, Weights
from pyodas2.systems import Beamformer


def test_init():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Beamformer(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    assert testee.num_sources == NUM_SOURCES
    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Beamformer(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    with pytest.raises(ValueError, match='The number of channels of the input must be 4.'):
        testee.process(Freqs('', NUM_CHANNELS + 1, NUM_BINS),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
                       Freqs('', NUM_SOURCES, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the input must be 8.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS + 1),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
                       Freqs('', NUM_SOURCES, NUM_BINS))

    with pytest.raises(ValueError, match='The number of sources of the weights must be 2.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Weights('', NUM_SOURCES + 1, NUM_CHANNELS, NUM_BINS),
                       Freqs('', NUM_SOURCES, NUM_BINS))

    with pytest.raises(ValueError, match='The number of channels of the weights must be 4.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Weights('', NUM_SOURCES, NUM_CHANNELS + 1, NUM_BINS),
                       Freqs('', NUM_SOURCES, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the weights must be 8.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS + 1),
                       Freqs('', NUM_SOURCES, NUM_BINS))

    with pytest.raises(ValueError, match='The number of channels of the output must be 2.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
                       Freqs('', NUM_SOURCES + 1, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the output must be 8.'):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
                       Freqs('', NUM_SOURCES, NUM_BINS + 1))


def test_process():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 5

    testee = Beamformer(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    in_freqs = Freqs('Xs', NUM_CHANNELS, NUM_BINS)
    weights = Weights('Ms', NUM_SOURCES, NUM_CHANNELS, NUM_BINS)
    out_freqs = Freqs('Ys', NUM_SOURCES, NUM_BINS)

    in_freqs.load_numpy(np.array(
        [[+1.0 - 2.0j, -2.0 + 1.0j, +3.0 - 1.0j, +1.0 + 2.0j, -2.0 + 0.0j],
         [-1.0 - 1.0j, +1.0 + 0.0j, -2.0 + 2.0j, +2.0 + 1.0j, -1.0 + 1.0j],
         [+0.0 + 3.0j, -1.0 - 1.0j, +1.0 + 0.0j, +0.0 + 1.0j, -1.0 + 1.0j],
         [+0.0 + 0.0j, -1.0 + 3.0j, +2.0 - 2.0j, +4.0 + 1.0j, -1.0 + 3.0j]], dtype=np.complex64))

    weights.load_numpy(np.array(
        [[[+2.0 - 1.0j, -1.0 + 2.0j, +0.0 - 1.0j, +2.0 + 2.0j, +1.0 - 1.0j],
          [-2.0 + 4.0j, -3.0 - 2.0j, +1.0 + 3.0j, -2.0 - 2.0j, +0.0 + 1.0j],
          [+1.0 + 1.0j, -1.0 + 1.0j, +0.0 - 2.0j, +0.0 - 1.0j, +1.0 + 1.0j],
          [+0.0 + 2.0j, +3.0 + 0.0j, -2.0 + 0.0j, -1.0 - 2.0j, -1.0 + 2.0j]],

         [[+0.0 + 1.0j, +2.0 + 1.0j, -2.0 - 2.0j, +1.0 + 1.0j, -1.0 + 0.0j],
          [-2.0 + 2.0j, -1.0 - 4.0j, +2.0 + 4.0j, -1.0 - 4.0j, +2.0 + 0.0j],
          [+2.0 + 0.0j, -2.0 + 1.0j, +1.0 - 2.0j, +2.0 - 2.0j, -3.0 + 0.0j],
          [-2.0 + 0.0j, +1.0 + 3.0j, +1.0 + 2.0j, -2.0 - 1.0j, -3.0 - 1.0j]]], dtype=np.complex64))

    testee.process(in_freqs, weights, out_freqs)

    expected_out_freqs = np.array(
        [[+5.0 + 6.0j, -2.0 + 16.0j, +1.0 + 17.0j, -7.0 + 11.0j, +6.0 + 0.0j],
         [-2.0 + 9.0j, +5.0 + 17.0j, -1.0 + 16.0j, -14.0 + 12.0j, +3.0 - 11.0j]], dtype=np.complex64)

    print(expected_out_freqs)
    print(out_freqs.to_numpy())

    assert np.allclose(out_freqs.to_numpy(), expected_out_freqs)


def test_repr():
    testee = Beamformer(2, 4, 8)
    assert repr(testee) == '<pyodas2.systems.Beamformer (S=2, C=4, B=8)>'
