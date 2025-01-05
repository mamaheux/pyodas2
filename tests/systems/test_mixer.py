import numpy as np
import pytest

from pyodas2.signals import Hops
from pyodas2.systems import Mixer


def test_init():
    testee = Mixer([0, 3])

    assert testee.num_channels == 2


def test_process_invalid_inputs():
    NUM_SHIFT = 5
    MAPPING = [0, 3]

    testee = Mixer(MAPPING)

    with pytest.raises(ValueError, match='hops_in does not have enough channels.'):
        testee.process(Hops('in', max(MAPPING), NUM_SHIFT),
                       Hops('ou', len(MAPPING), NUM_SHIFT))

    with pytest.raises(ValueError, match='hops_out does not have the same number of channels as the mixer.'):
        testee.process(Hops('in', max(MAPPING) + 1, NUM_SHIFT),
                       Hops('ou', len(MAPPING) + 1, NUM_SHIFT))


def test_process():
    NUM_SHIFT = 5
    MAPPING = [0, 3]

    testee = Mixer(MAPPING)
    hops_in = Hops('in', max(MAPPING) + 1, NUM_SHIFT)
    hops_out = Hops('out', len(MAPPING), NUM_SHIFT)

    hops_in.load_numpy(np.array([[0.0, 1.0, 2.0, 3.0, 4.0],
                                 [5.0, 6.0, 7.0, 8.0, 9.0],
                                 [9.0, 8.0, 7.0, 6.0, 5.0],
                                 [4.0, 3.0, 2.0, 1.0, 0.0]]))

    testee.process(hops_in, hops_out)

    expected_hops_out = np.array([[0.0, 1.0, 2.0, 3.0, 4.0],
                                  [4.0, 3.0, 2.0, 1.0, 0.0]])

    assert np.allclose(hops_out.to_numpy(), expected_hops_out)


def test_repr():
    testee = Mixer([0, 3])
    assert repr(testee) == '<pyodas2.systems.Mixer (C=2)>'
