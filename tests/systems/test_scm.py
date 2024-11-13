import pytest

import numpy as np

from pyodas2.systems import Scm
from pyodas2.signals import Covs, Freqs, Masks


def test_init():
    NUM_CHANNELS = 4
    NUM_BINS = 8
    ALPHA = 0.5

    testee = Scm(NUM_CHANNELS, NUM_BINS, ALPHA)

    assert testee.num_channels == NUM_CHANNELS
    assert testee.num_pairs == 6
    assert testee.num_bins == NUM_BINS
    assert testee.alpha == ALPHA


def test_process_invalid_inputs():
    NUM_CHANNELS = 4
    NUM_BINS = 8
    ALPHA = 0.5

    testee = Scm(NUM_CHANNELS, NUM_BINS, ALPHA)

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS + 1, NUM_BINS),
                       Masks('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS + 1),
                       Masks('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Masks('', NUM_CHANNELS + 1, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Masks('', NUM_CHANNELS, NUM_BINS + 1),
                       Covs('', NUM_CHANNELS, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Masks('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS + 1, NUM_BINS))

    with pytest.raises(ValueError):
        testee.process(Freqs('', NUM_CHANNELS, NUM_BINS),
                       Masks('', NUM_CHANNELS, NUM_BINS),
                       Covs('', NUM_CHANNELS, NUM_BINS + 1))



def test_process():
    NUM_CHANNELS = 3
    NUM_BINS = 4
    ALPHA = 0.1

    testee = Scm(NUM_CHANNELS, NUM_BINS, ALPHA)

    freqs = Freqs('', NUM_CHANNELS, NUM_BINS)
    masks = Masks('', NUM_CHANNELS, NUM_BINS)
    covs = Covs('', NUM_CHANNELS, NUM_BINS)

    masks.set_ones()

    freqs.load_numpy(np.array(
        [[+1.0 + 2.0j, -1.0 + 0.0j, +3.0 - 2.0j, +0.0 + 1.0j],
         [+0.0 - 2.0j, +2.0 + 2.0j, +1.0 + 1.0j, -2.0 - 1.0j],
         [+2.0 + 0.0j, +3.0 + 2.0j, +1.0 + 1.0j, -1.0 - 2.0j]], dtype=np.complex64))
    testee.process(freqs, masks, covs)


    expected_xcorrs = np.array(
        [[-0.4 + 0.2j, +0.2 + 0.4j, +0.0 - 0.4j],
         [-0.2 + 0.2j, -0.3 + 0.2j, +1.0 + 0.2j],
         [+0.1 - 0.5j, +0.1 - 0.5j, +0.2 + 0.0j],
         [-0.1 - 0.2j, -0.2 - 0.1j, +0.4 - 0.3j]], dtype=np.complex64).T
    expected_acorrs = np.array(
        [[0.5, 0.4, 0.4],
         [0.1, 0.8, 1.3],
         [1.3, 0.2, 0.2],
         [0.1, 0.5, 0.5]], dtype=np.float32).T

    assert np.allclose(covs.xcorrs_to_numpy(), expected_xcorrs)
    assert np.allclose(covs.acorrs_to_numpy(), expected_acorrs)


def test_repr():
    testee = Scm(4, 8, 0.5)
    assert repr(testee) == '<pyodas2.systems.Scm (C=4, B=8, A=0.5)>'
