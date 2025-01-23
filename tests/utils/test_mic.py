import pytest

from pyodas2.types import Xyz
from pyodas2.utils import Mic


def test_init_omnidirectional():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.OMNIDIRECTIONAL)

    assert testee.position.x == 1.0
    assert testee.position.y == 2.0
    assert testee.position.z == 3.0

    assert testee.direction.x == pytest.approx(-0.26726123690605164)
    assert testee.direction.y == pytest.approx(-0.5345224738121033)
    assert testee.direction.z == pytest.approx(-0.8017836809158325)

    assert testee.pattern == Mic.Pattern.OMNIDIRECTIONAL


def test_init_cardioid():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.CARDIOID)

    assert testee.position.x == 1.0
    assert testee.position.y == 2.0
    assert testee.position.z == 3.0

    assert testee.direction.x == pytest.approx(-0.26726123690605164)
    assert testee.direction.y == pytest.approx(-0.5345224738121033)
    assert testee.direction.z == pytest.approx(-0.8017836809158325)

    assert testee.pattern == Mic.Pattern.CARDIOID


def test_gain():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.OMNIDIRECTIONAL)
    assert testee.gain(Xyz(-1.0, -2.0, -3.0)) == pytest.approx(1.0)


def test_repr():
    testee = Mic(Xyz(1.0, 2.0, 3.0), Xyz(-1.0, -2.0, -3.0), Mic.Pattern.OMNIDIRECTIONAL)
    assert repr(testee) == '<pyodas2.utils.Mic (P=(1,2,3), D=(-0.267261,-0.534522,-0.801784), omnidirectional)>'
