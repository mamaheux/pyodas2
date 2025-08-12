import numpy as np
import pytest

from pyodas2.signals import Freqs, Weights
from pyodas2.systems import Beamformer


def test_init_not_enough_sources():
    Beamformer(1, 4, 8)
    with pytest.raises(ValueError, match='Number of sources must be at least 1.'):
        Beamformer(0, 4, 8)


def test_init_not_enough_channels():
    Beamformer(2, 1, 8)
    with pytest.raises(ValueError, match='Number of channels must be at least 1.'):
        Beamformer(2, 0, 8)


def test_init_not_enough_bins():
    Beamformer(2, 4, 1)
    with pytest.raises(ValueError, match='Number of bins must be at least 1.'):
        Beamformer(2, 4, 0)


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

    with pytest.raises(
        ValueError, match='Number of channels in input must match the number of channels in the beamformer.'
    ):
        testee.process(
            Freqs('', NUM_CHANNELS + 1, NUM_BINS),
            Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
            Freqs('', NUM_SOURCES, NUM_BINS),
        )

    with pytest.raises(ValueError, match='Number of bins in input must match the number of bins in the beamformer.'):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS + 1),
            Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
            Freqs('', NUM_SOURCES, NUM_BINS),
        )

    with pytest.raises(
        ValueError, match='Number of sources in weights must match the number of sources in the beamformer.'
    ):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS),
            Weights('', NUM_SOURCES + 1, NUM_CHANNELS, NUM_BINS),
            Freqs('', NUM_SOURCES, NUM_BINS),
        )

    with pytest.raises(
        ValueError, match='Number of channels in weights must match the number of channels in the beamformer.'
    ):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS),
            Weights('', NUM_SOURCES, NUM_CHANNELS + 1, NUM_BINS),
            Freqs('', NUM_SOURCES, NUM_BINS),
        )

    with pytest.raises(ValueError, match='Number of bins in weights must match the number of bins in the beamformer.'):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS),
            Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS + 1),
            Freqs('', NUM_SOURCES, NUM_BINS),
        )

    with pytest.raises(
        ValueError, match='Number of channels in output must match the number of sources in the beamformer.'
    ):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS),
            Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
            Freqs('', NUM_SOURCES + 1, NUM_BINS),
        )

    with pytest.raises(ValueError, match='Number of bins in output must match the number of bins in the beamformer.'):
        testee.process(
            Freqs('', NUM_CHANNELS, NUM_BINS),
            Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS),
            Freqs('', NUM_SOURCES, NUM_BINS + 1),
        )


def test_process():
    NUM_SOURCES = 2
    NUM_CHANNELS = 4
    NUM_BINS = 5

    testee = Beamformer(NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    in_freqs = Freqs('Xs', NUM_CHANNELS, NUM_BINS)
    weights = Weights('Ms', NUM_SOURCES, NUM_CHANNELS, NUM_BINS)
    out_freqs = Freqs('Ys', NUM_SOURCES, NUM_BINS)

    in_freqs.load_numpy(
        np.array(
            [
                [+1.0 - 2.0j, -2.0 + 1.0j, +3.0 - 1.0j, +1.0 + 2.0j, -2.0 + 0.0j],
                [-1.0 - 1.0j, +1.0 + 0.0j, -2.0 + 2.0j, +2.0 + 1.0j, -1.0 + 1.0j],
                [+0.0 + 3.0j, -1.0 - 1.0j, +1.0 + 0.0j, +0.0 + 1.0j, -1.0 + 1.0j],
                [+0.0 + 0.0j, -1.0 + 3.0j, +2.0 - 2.0j, +4.0 + 1.0j, -1.0 + 3.0j],
            ],
            dtype=np.complex64,
        )
    )

    weights.load_numpy(
        np.array(
            [
                [
                    [+2.0 - 1.0j, -1.0 + 2.0j, +0.0 - 1.0j, +2.0 + 2.0j, +1.0 - 1.0j],
                    [-2.0 + 4.0j, -3.0 - 2.0j, +1.0 + 3.0j, -2.0 - 2.0j, +0.0 + 1.0j],
                    [+1.0 + 1.0j, -1.0 + 1.0j, +0.0 - 2.0j, +0.0 - 1.0j, +1.0 + 1.0j],
                    [+0.0 + 2.0j, +3.0 + 0.0j, -2.0 + 0.0j, -1.0 - 2.0j, -1.0 + 2.0j],
                ],
                [
                    [+0.0 + 1.0j, +2.0 + 1.0j, -2.0 - 2.0j, +1.0 + 1.0j, -1.0 + 0.0j],
                    [-2.0 + 2.0j, -1.0 - 4.0j, +2.0 + 4.0j, -1.0 - 4.0j, +2.0 + 0.0j],
                    [+2.0 + 0.0j, -2.0 + 1.0j, +1.0 - 2.0j, +2.0 - 2.0j, -3.0 + 0.0j],
                    [-2.0 + 0.0j, +1.0 + 3.0j, +1.0 + 2.0j, -2.0 - 1.0j, -3.0 - 1.0j],
                ],
            ],
            dtype=np.complex64,
        )
    )

    testee.process(in_freqs, weights, out_freqs)

    expected_out_freqs = np.array(
        [
            [+5.0 + 6.0j, -2.0 + 16.0j, +1.0 + 17.0j, -7.0 + 11.0j, +6.0 + 0.0j],
            [-2.0 + 9.0j, +5.0 + 17.0j, -1.0 + 16.0j, -14.0 + 12.0j, +3.0 - 11.0j],
        ],
        dtype=np.complex64,
    )

    print(expected_out_freqs)
    print(out_freqs.to_numpy())

    assert np.allclose(out_freqs.to_numpy(), expected_out_freqs)


def test_repr():
    testee = Beamformer(2, 4, 8)
    assert repr(testee) == '<pyodas2.systems.Beamformer (S=2, C=4, B=8)>'
