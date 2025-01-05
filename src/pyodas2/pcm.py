from typing import Optional

import numpy as np


def interleaved_pcm_to_numpy(data: bytes,
                             nchannels: int,
                             sample_width: Optional[int] = None,
                             dtype : Optional[np.dtype] = None) -> np.ndarray:
    """
    Converts interleaved pcm bytes to a PyODAS2 compatible numpy array.
    The sample_width or the dtype must be provided.

    :param data: The interleaved pcm bytes.
    :param nchannels: The number of channels.
    :param sample_width: The number of bytes per sample. The supported sample_width are 2 and 4.
    :param dtype: The numpy dtype. The supported dtypes are np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64, np.float32 and np.float64.
    :return: The compatible numpy array.
    """
    if sample_width is not None and dtype is not None:
        msg = 'The sample_width or the dtype must be provided, not both.'
        raise ValueError(msg)

    if sample_width is not None:
        if sample_width == 2:
            return np.frombuffer(data, dtype=np.int16).reshape(-1, nchannels).T
        if sample_width == 4:
            return np.frombuffer(data, dtype=np.int32).reshape(-1, nchannels).T

        msg = 'Not supported sample_width.'
        raise ValueError(msg)

    if dtype is not None:
        if np.issubdtype(dtype, np.integer) or np.issubdtype(dtype, np.floating):
            return np.frombuffer(data, dtype=dtype).reshape(-1, nchannels).T

        msg = 'Not supported dtype.'
        raise ValueError(msg)

    msg = 'The sample_width or the dtype must be provided.'
    raise ValueError(msg)


def numpy_to_interleaved_pcm(data: np.ndarray,
                             sample_width: Optional[int] = None,
                             dtype : Optional[np.dtype] = None) -> bytes:
    """
    Converts a PyODAS2 compatible numpy array to interleaved pcm bytes.
    The sample_width or the dtype must be provided.

    :param data: The numpy array to convert. The supported dtypes are np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64, np.float32 and np.float64.
    :param sample_width: The number of bytes per sample. The supported sample_width are 2 and 4.
    :param dtype: The numpy dtype for the output bytes. The supported dtypes are np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64, np.float32 and np.float64.
    :return: The interleaved pcm bytes.
    """
    if sample_width is not None and dtype is not None:
        msg = 'The sample_width or the dtype must be provided, not both.'
        raise ValueError(msg)
    if not np.issubdtype(data.dtype, np.integer) and not np.issubdtype(data.dtype, np.floating):
        msg = 'The data dtype is not supported.'
        raise ValueError(msg)

    if np.issubdtype(data.dtype, np.signedinteger):
        data = -data.astype(np.float32) / np.iinfo(data.dtype).min
    elif np.issubdtype(data.dtype, np.unsignedinteger):
        data = data.astype(np.float32) / np.iinfo(data.dtype).max - 0.5
    else:
        data = np.clip(data, a_min=-1.0, a_max=1.0)

    if sample_width is not None:
        if sample_width == 2:
            return (data * np.iinfo(np.int16).max).astype(np.int16).T.tobytes()
        if sample_width == 4:
            return (data * np.iinfo(np.int32).max).astype(np.int32).T.tobytes()

        msg = 'Not supported sample_width.'
        raise ValueError(msg)

    if dtype is not None:
        if np.issubdtype(dtype, np.integer):
            return (data * np.iinfo(dtype).max).astype(dtype).T.tobytes()
        if np.issubdtype(dtype, np.floating):
            return data.astype(dtype).T.tobytes()

        msg = 'Not supported dtype.'
        raise ValueError(msg)

    msg = 'The sample_width or the dtype must be provided.'
    raise ValueError(msg)
