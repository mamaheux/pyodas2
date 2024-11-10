import pytest

from pyodas2.signals import Doas
from pyodas2.types import Xyz

def test_init_too_long_label():
    Doas('1' * 63, 4)

    with pytest.raises(ValueError):
        Doas('1' * 64, 4)

def test_init():
    testee = Doas('potential', 4)

    assert testee.label == 'potential'
    assert len(testee) == 4


def test_get_item_out_of_range():
    testee = Doas('potential', 4)

    with pytest.raises(IndexError):
        a = testee[5]


def test_get_item_mutable():
    testee = Doas('potential', 4)
    testee[0].type = Doas.Src.POTENTIAL
    testee[1].coord = Xyz(-10.0, 0.0, 0.0)
    testee[2].energy = 2.0

    assert testee[0].type == Doas.Src.POTENTIAL
    assert testee[1].coord.x == -10.0
    assert testee[2].energy == 2.0

def test_set_item_out_of_range():
    testee = Doas('potential', 4)

    with pytest.raises(IndexError):
        testee[5] = Doas.Dir(Doas.Src.POTENTIAL, Xyz(11.0, 0.0, 0.0), 5.0)


def test_set_item():
    testee = Doas('potential', 4)
    testee[0] = Doas.Dir(Doas.Src.POTENTIAL, Xyz(11.0, 0.0, 0.0), 5.0)

    assert testee[0].type == Doas.Src.POTENTIAL
    assert testee[0].coord.x == 11.0
    assert testee[0].energy == 5.0


def test_repr():
    testee = Doas('potential', 4)
    assert repr(testee) == '<pyodas2.signals.Doas (potential, len=4)>'
    assert repr(testee[0]) == '<pyodas2.signals.Doas.Dir ((0,0,0), T=0, E=0)>'
