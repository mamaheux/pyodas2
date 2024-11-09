import pytest

from pyodas2.utils import Mic
from pyodas2.types import Xyz


def test_init_omnidirectional():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.Omnidirectional)

    assert testee.position.x == 1.0
    assert testee.position.y == 2.0
    assert testee.position.z == 3.0

    assert testee.direction.x == -1.0
    assert testee.direction.y == -2.0
    assert testee.direction.z == -3.0

    assert testee.pattern == Mic.Pattern.Omnidirectional


def test_init_cardioid():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.Cardioid)

    assert testee.position.x == 1.0
    assert testee.position.y == 2.0
    assert testee.position.z == 3.0

    assert testee.direction.x == -1.0
    assert testee.direction.y == -2.0
    assert testee.direction.z == -3.0

    assert testee.pattern == Mic.Pattern.Cardioid


def test_gain():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.Omnidirectional)
    assert testee.gain(Xyz(-1.0, -2.0, -3.0)) == pytest.approx(1.0)


def test_repr():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.Omnidirectional)
    assert repr(testee) == '<pyodas2.utils.Mic (P=(1,2,3), D=(-1,-2,-3), omnidirectional)>'


def test_str():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.Cardioid)
    assert str(testee) == 'P=(1,2,3), D=(-1,-2,-3), cardioid'
