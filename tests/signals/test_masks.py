import numpy as np
import pytest

from pyodas2.signals import Masks


def test_init_too_long_label():
    Masks('1' * 63, 4, 512)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Masks('1' * 64, 4, 512)

def test_init():
    testee = Masks('Ms', 4, 512)

    assert testee.label == 'Ms'
    assert testee.num_channels == 4
    assert testee.num_bins == 512


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_numpy_invalid_dtype(dtype):
    testee = Masks('Ms', 2, 4)

    with pytest.raises(ValueError, match='Invalid array shape, it must be *.'):
        testee.load_numpy(np.zeros(8, dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((1, 4), dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((2, 6), dtype=dtype))


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_numpy(dtype):
    testee = Masks('Ms', 2, 4)

    input_data = np.array([[1.0, 2.0, 3.0, 4.0],
                           [5.0, 6.0, 7.0, 8.0]], dtype=dtype)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = input_data.astype(np.float32)
    assert np.allclose(output_data, expected_data)


def test_set_zeros():
    testee = Masks('Ms', 2, 4)

    input_data = np.array([[1.0, 2.0, 3.0, 4.0],
                           [5.0, 6.0, 7.0, 8.0]], dtype=np.float32)
    testee.load_numpy(input_data)
    testee.set_zeros()
    assert np.allclose(testee.to_numpy(), np.zeros((2, 4), dtype=np.float32))


def test_set_ones():
    testee = Masks('Ms', 2, 4)

    input_data = np.array([[1.0, 2.0, 3.0, 4.0],
                           [5.0, 6.0, 7.0, 8.0]], dtype=np.float32)
    testee.load_numpy(input_data)
    testee.set_ones()
    assert np.allclose(testee.to_numpy(), np.ones((2, 4), dtype=np.float32))


def test_repr():
    testee = Masks('Ms', 2, 4)
    assert repr(testee) == '<pyodas2.signals.Masks (Ms, C=2, B=4)>'
