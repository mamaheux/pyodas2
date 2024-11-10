import pytest

import numpy as np

from pyodas2.signals import Hops

def test_init_too_long_label():
    Hops('1' * 63, 4, 512)

    with pytest.raises(ValueError):
        Hops('1' * 64, 4, 512)

def test_init():
    testee = Hops('xs', 4, 512)

    assert testee.label == 'xs'
    assert testee.num_channels == 4
    assert testee.num_shifts == 512
    assert testee.num_samples == 512

@pytest.mark.parametrize("dtype", [np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64, np.float32, np.float64])
def test_numpy_invalid_shape_int(dtype):
    testee = Hops('xs', 2, 4)

    with pytest.raises(ValueError):
        testee.load_numpy(np.zeros(8, dtype=dtype))

    with pytest.raises(ValueError):
        testee.load_numpy(np.zeros((1, 4), dtype=dtype))

    with pytest.raises(ValueError):
        testee.load_numpy(np.zeros((2, 6), dtype=dtype))


def test_numpy_int8():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-128, -64, 0, 64],
                     [127, 64, 0, -64]], dtype=np.int8)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [0.9921875, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_int16():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-32768, -16384, 0, 16384],
                           [32767, 16384, 0, -16384]], dtype=np.int16)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 0.9999695, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_int32():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-2147483648, -1073741824, 0, 1073741824],
                           [2147483647, 1073741824, 0, -1073741824]], dtype=np.int32)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_int64():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-2147483648 << 32, -1073741824 << 32, 0, 1073741824 << 32],
                           [2147483647 << 32, 1073741824 << 32, 0 << 32, -1073741824 << 32]], dtype=np.int64)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_uint8():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[0, 64, 128, 192],
                           [255, 192, 128, 64]], dtype=np.uint8)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.4980392, 0.00392163, 0.5058825],
                              [1.0, 0.5058825, 0.00392163, -0.4980392]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_uint16():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[0, 16384, 32768, 49152],
                           [65535, 49152, 32768, 16384]], dtype=np.uint16)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0000000e+00, -4.9999237e-01,  1.5258789e-05,  5.0002289e-01],
                              [  1.0000000e+00,  5.0002289e-01,  1.5258789e-05, -4.9999237e-01]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_uint32():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[0, 1073741824, 2147483648, 3221225472],
                           [4294967295, 3221225472, 2147483648, 1073741824]], dtype=np.uint32)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_uint64():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[0 << 32, 1073741824 << 32, 2147483648 << 32, 3221225472 << 32],
                           [4294967295 << 32, 3221225472 << 32, 2147483648 << 32, 1073741824 << 32]], dtype=np.uint64)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_float32():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                           [1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_numpy_float64():
    testee = Hops('xs', 2, 4)

    input_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                           [1.0, 0.5, 0.0, -0.5]], dtype=np.float64)
    testee.load_numpy(input_data)
    output_data = testee.to_numpy()
    assert output_data.dtype == np.float32

    expected_data = np.array([[-1.0, -0.5, 0.0, 0.5],
                              [ 1.0, 0.5, 0.0, -0.5]], dtype=np.float32)
    assert np.allclose(output_data, expected_data)


def test_repr():
    testee = Hops('xs', 2, 4)
    assert repr(testee) == '<pyodas2.signals.Hops (xs, C=2, S=4)>'
