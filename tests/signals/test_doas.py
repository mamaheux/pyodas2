import pytest

from pyodas2.signals import Doas
from pyodas2.types import Xyz


def test_init_too_long_label():
    Doas('1' * 63, 4)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Doas('1' * 64, 4)

def test_init():
    testee = Doas('potential', 4)

    assert testee.label == 'potential'
    assert len(testee) == 4


def test_get_item_out_of_range():
    testee = Doas('potential', 4)

    with pytest.raises(IndexError):
        _a = testee[5]


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


def test_dir_copy():
    testee = Doas.Dir(Doas.Src.POTENTIAL, Xyz(1.0, 2.0, 3.0), 5.0)
    testee_copy = testee.copy()

    testee.type = Doas.Src.UNDEFINED
    testee.coord.x = -1.0
    testee.coord.y = -2.0
    testee.coord.z = -3.0
    testee.energy = 10.0

    assert testee_copy.type == Doas.Src.POTENTIAL
    assert testee_copy.coord.x == 1.0
    assert testee_copy.coord.y == 2.0
    assert testee_copy.coord.z == 3.0
    assert testee_copy.energy == 5.0
