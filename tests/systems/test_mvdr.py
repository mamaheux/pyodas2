import numpy as np
import pytest

from pyodas2.signals import Covs, Weights
from pyodas2.systems import Mvdr


def test_init_not_enough_channels():
    Mvdr(2, 8)
    with pytest.raises(ValueError, match='Number of channels must be at least 2.'):
        Mvdr(1, 8)


def test_init_not_enough_bins():
    Mvdr(4, 1)
    with pytest.raises(ValueError, match='Number of bins must be at least 1.'):
        Mvdr(4, 0)


def test_init():
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Mvdr(NUM_CHANNELS, NUM_BINS)

    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_SOURCES = 1
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Mvdr(NUM_CHANNELS, NUM_BINS)

    with pytest.raises(ValueError, match='Number of channels in covs must match the number of channels in the MVDR.'):
        testee.process(Covs('', NUM_CHANNELS + 1, NUM_BINS), Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='Number of bins in covs must match the number of bins in the MVDR.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS + 1), Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='Number of sources in weights must match the number of sources in the MVDR'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS), Weights('', NUM_SOURCES + 1, NUM_CHANNELS, NUM_BINS))

    with pytest.raises(
        ValueError, match='Number of channels in weights must match the number of channels in the MVDR.'
    ):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS), Weights('', NUM_SOURCES, NUM_CHANNELS + 1, NUM_BINS))

    with pytest.raises(ValueError, match='Number of bins in weights must match the number of bins in the MVDR.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS), Weights('', NUM_SOURCES, NUM_CHANNELS, NUM_BINS + 1))


def test_process():
    NUM_SOURCES = 1
    NUM_CHANNELS = 4
    NUM_BINS = 2

    testee = Mvdr(NUM_CHANNELS, NUM_BINS)

    covs = Covs('XXs', NUM_CHANNELS, NUM_BINS)
    weights = Weights('Ws', NUM_SOURCES, NUM_CHANNELS, NUM_BINS)

    covs.xcorrs_load_numpy(
        np.array(
            [
                [-8.0 + 4.0j, -4.0 + 8.0j],
                [+6.0 - 8.0j, +4.0 + 12.0j],
                [-11.0 - 7.0j, -8.0 - 4.0j],
                [-8.0 + 4.0j, +10.0 - 10.0j],
                [+6.0 + 10.0j, +0.0 + 10.0j],
                [-1.0 - 13.0j, +10.0 + 0.0j],
            ],
            dtype=np.complex64,
        )
    )
    covs.acorrs_load_numpy(np.array([[+10.0, +8.0], [+8.0, +10.0], [+10.0, +20.0], [+17.0, +10.0]], dtype=np.float32))

    testee.process(covs, weights)

    expected_weights = np.array(
        [
            [
                [+0.2222 + 0.0000j, +0.1667 + 0.0000j],
                [-0.1778 - 0.0889j, -0.0833 - 0.1667j],
                [+0.1333 + 0.1778j, +0.0833 - 0.2500j],
                [-0.2444 + 0.1556j, -0.1667 + 0.0833j],
            ]
        ],
        dtype=np.complex64,
    )

    assert np.allclose(weights.to_numpy(), expected_weights, atol=1e-3)


def test_repr():
    testee = Mvdr(4, 8)
    assert repr(testee) == '<pyodas2.systems.Mvdr (C=4, B=8)>'
