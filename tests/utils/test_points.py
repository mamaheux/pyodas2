import pytest

from pyodas2.utils import Points


def test_len():
    sphere = Points(Points.Geometry.Sphere)
    assert len(sphere) == 2562

    halfsphere = Points(Points.Geometry.Halfsphere)
    assert len(halfsphere) == 1321

    arc = Points(Points.Geometry.Arc)
    assert len(arc) == 181


def test_get_item_out_of_range():
    sphere = Points(Points.Geometry.Sphere)
    i = 0
    for i, _ in enumerate(sphere):
        pass

    assert i == 2561


def test_get_item():
    sphere = Points(Points.Geometry.Sphere)
    p3 = sphere[3]

    assert p3.x == pytest.approx(0.040640)
    assert p3.y == pytest.approx(-0.055937)
    assert p3.z == pytest.approx(0.997607)


def test_repr():
    testee = Points(Points.Geometry.Arc)
    assert repr(testee) == '<pyodas2.utils.Points (len=181)>'


def test_str():
    testee = Points(Points.Geometry.Arc)
    assert str(testee).startswith('[(1,0,0),')
    assert str(testee).endswith(')]')
