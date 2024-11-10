import pytest

import numpy as np

from pyodas2.signals import Covs

def test_init_too_long_label():
    Covs('1' * 63, 4, 512)

    with pytest.raises(ValueError):
        Covs('1' * 64, 4, 512)

def test_init():
    testee = Covs('XXs', 4, 512)

    assert testee.label == 'XXs'
    assert testee.num_channels == 4
    assert testee.num_pairs == 6
    assert testee.num_bins == 512


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_numpy_xcorrs_invalid_shape(dtype):
    testee = Covs('XXs', 4, 2)

    with pytest.raises(ValueError):
        testee.xcorrs_load_numpy(np.zeros(12, dtype=dtype))

    with pytest.raises(ValueError):
        testee.xcorrs_load_numpy(np.zeros((5, 2), dtype=dtype))

    with pytest.raises(ValueError):
        testee.xcorrs_load_numpy(np.zeros((6, 3), dtype=dtype))


@pytest.mark.parametrize("dtype", [np.complex64, np.complex128])
def test_xcorrs_numpy(dtype):
    testee = Covs('XXs', 4, 2)

    input_data = np.array([[1.0 + 2.0j, 2.0 + 3.0j],
                           [4.0 + 5.0j, 6.0 + 7.0j],
                           [7.0 + 6.0j, 5.0 + 4.0j],
                           [3.0 + 2.0j, 1.0 + 0.0j],
                           [8.0 + 9.0j, 9.0 + 8.0j],
                           [3.0 + 7.0j, 1.0 + 6.0j]], dtype=dtype)
    testee.xcorrs_load_numpy(input_data)
    output_data = testee.xcorrs_to_numpy()
    assert output_data.dtype == np.complex64

    expected_data = input_data.astype(np.complex64)
    assert np.allclose(output_data, expected_data)


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_numpy_acorrs_invalid_shape(dtype):
    testee = Covs('XXs', 2, 4)

    with pytest.raises(ValueError):
        testee.acorrs_load_numpy(np.zeros(12, dtype=dtype))

    with pytest.raises(ValueError):
        testee.acorrs_load_numpy(np.zeros((3, 4), dtype=dtype))

    with pytest.raises(ValueError):
        testee.acorrs_load_numpy(np.zeros((2, 5), dtype=dtype))


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_acorrs_numpy(dtype):
    testee = Covs('XXs', 2, 4)

    input_data = np.array([[1.0, 2.0, 3.0, 4.0],
                           [5.0, 6.0, 7.0, 8.0]], dtype=dtype)
    testee.acorrs_load_numpy(input_data)
    output_data = testee.acorrs_to_numpy()
    assert output_data.dtype == np.float32

    expected_data = input_data.astype(np.float32)
    assert np.allclose(output_data, expected_data)


def test_repr():
    testee = Covs('XXs', 4, 512)
    assert repr(testee) == '<pyodas2.signals.Covs (XXs, C=4, P=6, B=512)>'
