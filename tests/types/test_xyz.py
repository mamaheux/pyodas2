import pytest

from pyodas2.types import Xyz


def test_init():
    testee = Xyz(1.0, 2.0, 3.0)
    assert testee.x == 1.0
    assert testee.y == 2.0
    assert testee.z == 3.0


def test_unit():
    a = Xyz(1.0, 2.0, 3.0)
    unit = a.unit()
    assert unit.x == pytest.approx(0.26726123690605164)
    assert unit.y == pytest.approx(0.53452247381)
    assert unit.z == pytest.approx(0.80178371071)


def test_mag():
    a = Xyz(3.0, 4.0, 5.0)
    assert a.mag() == pytest.approx(7.071067810058594)


def test_l2():
    a = Xyz(3.0, 4.0, 5.0)
    assert a.l2() == 50


def test_dot():
    a = Xyz(2.0, 3.0, 4.0)
    b = Xyz(-2.0, -3.0, -4.0)
    dot = a.dot(b)
    assert dot == -29.0


def test_cross():
    a = Xyz(1.0, 0.0, 0.0)
    b = Xyz(0.0, 1.0, 0.0)
    cross = a.cross(b)

    assert cross.x == 0.0
    assert cross.y == 0.0
    assert cross.z == 1.0


def test_add():
    a = Xyz(1.0, 2.0, 3.0)
    b = Xyz(2.0, 3.0, 4.0)
    sum = a + b

    assert sum.x == 3.0
    assert sum.y == 5.0
    assert sum.z == 7.0


def test_sub():
    a = Xyz(1.0, 3.0, 6.0)
    b = Xyz(2.0, 2.0, 4.0)
    sum = a - b

    assert sum.x == -1.0
    assert sum.y == 1.0
    assert sum.z == 2.0


def test_mult():
    a = Xyz(1.0, 2.0, 3.0)
    scaled_a = a * 2
    assert scaled_a.x == 2.0
    assert scaled_a.y == 4.0
    assert scaled_a.z == 6.0

    b = Xyz(2.0, 3.0, 4.0)
    scaled_b = 3 * b
    assert scaled_b.x == 6.0
    assert scaled_b.y == 9.0
    assert scaled_b.z == 12.0


def test_inverse():
    a = Xyz(1.0, -2.0, 3.0)
    inverse = -a

    assert inverse.x == -1.0
    assert inverse.y == 2.0
    assert inverse.z == -3.0


def test_repr():
    a = Xyz(1.0, 2.0, 3.0)
    assert repr(a) == '<pyodas2.types.Xyz (1,2,3)>'


def test_str():
    a = Xyz(1.0, 2.0, 3.0)
    assert str(a) == '(1,2,3)'
