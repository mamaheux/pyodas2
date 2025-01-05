import numpy as np
import pytest

from pyodas2.signals import Freqs


def test_init_too_long_label():
    Freqs('1' * 63, 4, 512)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Freqs('1' * 64, 4, 512)

def test_init():
    testee = Freqs('Xs', 4, 512)

    assert testee.label == 'Xs'
    assert testee.num_channels == 4
    assert testee.num_bins == 512


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_numpy_invalid_shape(dtype):
    testee = Freqs('xs', 2, 4)

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros(8, dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((1, 4), dtype=dtype))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        testee.load_numpy(np.zeros((2, 6), dtype=dtype))


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_numpy(dtype):
    testee = Freqs('Xs', 2, 4)

    input_data = np.array([[1.0 + 2.0j, 2.0 + 3.0j, 4.0 + 5.0j, 6.0 + 7.0j],
                           [7.0 + 6.0j, 5.0 + 4.0j, 3.0 + 2.0j, 1.0 + 0.0j]], dtype=dtype)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.complex64

    expected_data = input_data.astype(np.complex64)
    assert np.allclose(output_data, expected_data)


def test_repr():
    testee = Freqs('Xs', 2, 4)
    assert repr(testee) == '<pyodas2.signals.Freqs (Xs, C=2, B=4)>'
