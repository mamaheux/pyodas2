import numpy as np
import pytest

from pyodas2.signals import Imgs


def test_init_too_long_label():
    Imgs('1' * 63, 1000, 2)

    with pytest.raises(ValueError, match='Label must be a string with less than 64 characters.'):
        Imgs('1' * 64, 1000, 2)


def test_init_not_enough_points():
    Imgs('test', 1, 2)

    with pytest.raises(ValueError, match='Number of points must be at least 1.'):
        Imgs('test', 0, 2)


def test_init_not_enough_directions():
    Imgs('test', 1000, 1)

    with pytest.raises(ValueError, match='Number of directions must be at least 1.'):
        Imgs('test', 1000, 0)


def test_init():
    imgs = Imgs('test', 1000, 2)
    assert imgs.label == 'test'
    assert imgs.num_points == 1000
    assert imgs.num_directions == 2


def test_numpy_invalid_shape():
    imgs = Imgs('test', 1000, 2)

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        imgs.load_numpy(np.zeros((3, 1000), dtype=np.float32))

    with pytest.raises(ValueError, match='Invalid array shape, it must be *'):
        imgs.load_numpy(np.zeros((2, 999), dtype=np.float32))


def test_numpy():
    imgs = Imgs('test', 1000, 2)
    array = np.random.rand(2, 1000).astype(np.float32)
    imgs.load_numpy(array)

    assert imgs.to_numpy().shape == (2, 1000)
    np.testing.assert_array_equal(imgs.to_numpy(), array)


def test_repr():
    imgs = Imgs('test', 1000, 2)
    assert repr(imgs) == '<pyodas2.signals.Img (test, D=2, P=1000)>'
