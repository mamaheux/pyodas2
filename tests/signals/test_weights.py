import numpy as np
import pytest

from pyodas2.signals import Weights


def test_init_too_long_label():
    Weights('1' * 63, 2, 4, 512)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Weights('1' * 64, 2, 4, 512)

def test_init():
    testee = Weights('Ws', 2, 4, 512)

    assert testee.label == 'Ws'
    assert testee.num_sources == 2
    assert testee.num_channels == 4
    assert testee.num_bins == 512


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_numpy_invalid_shape(dtype):
    testee = Weights('Ws', 2, 4, 8)

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros(64, dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((1, 4), dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((1, 4, 8), dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((2, 3, 8), dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((2, 4, 7), dtype=dtype))


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_numpy(dtype):
    testee = Weights('Ws', 2, 4, 8)

    input_data = (np.random.randn(2, 4, 8) + 1j * np.random.randn(2, 4, 8)).astype(dtype)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.complex64

    expected_data = input_data.astype(np.complex64)
    assert np.allclose(output_data, expected_data)


def test_repr():
    testee = Weights('Ws', 2, 4, 8)
    assert repr(testee) == '<pyodas2.signals.Weights (Ws, S=2, C=4, B=8)>'
