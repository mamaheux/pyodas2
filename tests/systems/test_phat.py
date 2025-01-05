import numpy as np
import pytest

from pyodas2.signals import Covs
from pyodas2.systems import Phat


def test_init():
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Phat(NUM_CHANNELS, NUM_BINS)

    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_pairs == 6
    assert testee.num_bins == NUM_BINS


def test_process_invalid_inputs():
    NUM_CHANNELS = 4
    NUM_BINS = 8

    testee = Phat(NUM_CHANNELS, NUM_BINS)

    with pytest.raises(ValueError, match='The number of channels of the input must be 4.'):
        testee.process(Covs('', NUM_CHANNELS + 1, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the input must be 8.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS + 1),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError, match='The number of channels of the output must be 4.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS + 1, NUM_BINS))

    with pytest.raises(ValueError, match='The number of bins of the output must be 8.'):
        testee.process(Covs('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS + 1))


def test_process():
    NUM_CHANNELS = 3
    NUM_BINS = 4

    testee = Phat(NUM_CHANNELS, NUM_BINS)

    covs_in = Covs('XXs', NUM_CHANNELS, NUM_BINS)
    covs_out = Covs('XXps', NUM_CHANNELS, NUM_BINS)

    covs_in.xcorrs_load_numpy(np.array(
        [[+2.0 + 1.0j, -3.0 + 2.0j, +1.0 - 2.0j, +2.0 - 1.0j],
         [+1.0 - 3.0j, -2.0 + 1.0j, +4.0 + 2.0j, -1.0 + 1.0j],
         [-2.0 + 2.0j, +0.0 + 0.0j, -1.0 + 2.0j, -3.0 + 1.0j]], dtype=np.complex64)),
    covs_in.acorrs_load_numpy(np.array(
        [[+2.0, +1.0, +3.0, +2.0],
         [+1.0, +2.0, +1.0, +3.0],
         [+2.0, +2.0, +2.0, +4.0]], dtype=np.float32)),

    testee.process(covs_in, covs_out)

    expected_xcorrs = np.array(
        [[1.0, 1.0, 1.0, 1.0],
         [1.0, 1.0, 1.0, 1.0],
         [1.0, 0.0, 1.0, 1.0]], dtype=np.float32)

    print(np.abs(covs_out.xcorrs_to_numpy()))
    print(np.ones((3, 4), dtype=np.float32))
    assert np.allclose(np.abs(covs_out.xcorrs_to_numpy()), expected_xcorrs)
    assert np.allclose(covs_out.acorrs_to_numpy(), np.ones((3, 4), dtype=np.float32), atol=1e-3)


def test_repr():
    testee = Phat(4, 8)
    assert repr(testee) == '<pyodas2.systems.Phat (C=4, B=8)>'
