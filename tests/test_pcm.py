import numpy as np
import pytest

from pyodas2.pcm import interleaved_pcm_to_numpy, numpy_to_interleaved_pcm


def test_interleaved_pcm_to_numpy_invalid_inputs():
    data = b'1234567801234567'
    nchannels = 2

    with pytest.raises(ValueError, match='The sample_width or the dtype must be provided, not both.'):
        interleaved_pcm_to_numpy(data, nchannels, sample_width=2, dtype=np.int32)

    with pytest.raises(ValueError, match='Not supported sample_width.'):
        interleaved_pcm_to_numpy(data, nchannels, sample_width=1)

    with pytest.raises(ValueError, match='Not supported dtype.'):
        interleaved_pcm_to_numpy(data, nchannels, dtype=np.complex64)

    with pytest.raises(ValueError, match='The sample_width or the dtype must be provided.'):
        interleaved_pcm_to_numpy(data, nchannels)


def test_interleaved_pcm_to_numpy_sample_width_2():
    data = b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
    nchannels = 2

    output = interleaved_pcm_to_numpy(data, nchannels, sample_width=2)
    expected_output = np.array([[1, 3, 5],
                                [2, 4, 6]], dtype=np.int16)

    assert np.allclose(output, expected_output)


def test_interleaved_pcm_to_numpy_sample_width_4():
    data = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00'
    nchannels = 2

    output = interleaved_pcm_to_numpy(data, nchannels, sample_width=4)
    expected_output = np.array([[1, 3, 5],
                                [2, 4, 6]], dtype=np.int32)

    assert np.allclose(output, expected_output)


def test_interleaved_pcm_to_numpy_dtype():
    data = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00'
    nchannels = 2

    output = interleaved_pcm_to_numpy(data, nchannels, dtype=np.int32)
    expected_output = np.array([[1, 3, 5],
                                [2, 4, 6]], dtype=np.int32)

    assert np.allclose(output, expected_output)


def test_numpy_to_interleaved_pcm_invalid_inputs():
    with pytest.raises(ValueError, match='The sample_width or the dtype must be provided, not both.'):
        numpy_to_interleaved_pcm(np.zeros((2, 3), dtype=np.float32), sample_width=2, dtype=np.int32)

    with pytest.raises(ValueError, match='The data dtype is not supported.'):
        numpy_to_interleaved_pcm(np.zeros((2, 3), dtype=np.complex64), sample_width=2)

    with pytest.raises(ValueError, match='Not supported sample_width.'):
        numpy_to_interleaved_pcm(np.zeros((2, 3), dtype=np.float32), sample_width=1)

    with pytest.raises(ValueError, match='Not supported dtype.'):
        numpy_to_interleaved_pcm(np.zeros((2, 3), dtype=np.float32), dtype=np.complex64)

    with pytest.raises(ValueError, match=r'The sample_width or the dtype must be provided.'):
        numpy_to_interleaved_pcm(np.zeros((2, 3), dtype=np.float32))


def test_numpy_to_interleaved_pcm_data_dtype_float32_sample_width_2():
    data = np.array([[1.0, 0.5, 0.0],
                    [0.0, -0.5, -1.0]], dtype=np.float32)
    output = numpy_to_interleaved_pcm(data, sample_width=2)

    assert output == b'\xff\x7f\x00\x00\xff?\x01\xc0\x00\x00\x01\x80'


def test_numpy_to_interleaved_pcm_data_dtype_int16_sample_width_4():
    data = np.array([[1, 3, 5],
                    [2, 4, 6]], dtype=np.int16)
    output = numpy_to_interleaved_pcm(data, sample_width=4)

    assert output == b'\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00'


def test_numpy_to_interleaved_pcm_data_dtype_uint8_dtype_float32():
    data = np.array([[0, 64, 128],
                    [255, 128, 64]], dtype=np.uint8)
    output = numpy_to_interleaved_pcm(data, dtype=np.float32)

    assert output == b'\x00\x00\x00\xbf\x00\x00\x00?\xfe\xfe~\xbe\x00\x81\x00;\x00\x81\x00;\xfe\xfe~\xbe'


def test_numpy_to_interleaved_pcm_data_dtype_float32_dtype_int16():
    data = np.array([[2.0, 0.5, 0.0],
                     [-1.0, -0.25, -0.125]], dtype=np.float32)
    output = numpy_to_interleaved_pcm(data, dtype=np.int16)

    assert output == b'\xff\x7f\x01\x80\xff?\x01\xe0\x00\x00\x01\xf0'
