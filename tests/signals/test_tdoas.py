import pytest

from pyodas2.signals import Tdoas


def test_init_too_long_label():
    Tdoas('1' * 63, 4, 2)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Tdoas('1' * 64, 4, 2)

def test_init():
    testee = Tdoas('tdoas', 4, 2)

    assert testee.label == 'tdoas'
    assert testee.shape == (2, 6)
    assert testee.num_sources == 2
    assert testee.num_channels == 4
    assert testee.num_pairs == 6


def test_get_item_out_of_range():
    testee = Tdoas('tdoas', 4, 2)

    with pytest.raises(IndexError):
        _a = testee[3, 0]

    with pytest.raises(IndexError):
        _a = testee[0, 6]


def test_get_item_mutable():
    testee = Tdoas('tdoas', 4, 2)
    testee[0, 0].delay = 10.0
    testee[0, 1].amplitude = 0.5

    assert testee[0, 0].delay == 10.0
    assert testee[0, 1].amplitude == 0.5


def test_set_item_out_of_range():
    testee = Tdoas('tdoas', 4, 2)

    with pytest.raises(IndexError):
        testee[3, 0] = Tdoas.Tau(1.0, 2.0)

    with pytest.raises(IndexError):
        testee[0, 6] = Tdoas.Tau(1.0, 2.0)


def test_set_item():
    testee = Tdoas('tdoas', 4, 2)
    testee[0, 0] = Tdoas.Tau(20.0, 10.0)

    assert testee[0, 0].delay == 20.0
    assert testee[0, 0].amplitude == 10.0


def test_repr():
    testee = Tdoas('tdoas', 4, 2)
    assert repr(testee) == '<pyodas2.signals.Tdoas (tdoas, C=4, S=2, P=6)>'
    assert repr(testee[0, 0]) == '<pyodas2.signals.Tdoas.Tau (D=0, A=0)>'
