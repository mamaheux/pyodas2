import pytest

from pyodas2.utils import Points


def test_len():
    sphere = Points(Points.Geometry.SPHERE)
    assert len(sphere) == 2562

    halfsphere = Points(Points.Geometry.HALFSPHERE)
    assert len(halfsphere) == 1321

    arc = Points(Points.Geometry.ARC)
    assert len(arc) == 181


def test_get_item_out_of_range():
    sphere = Points(Points.Geometry.SPHERE)
    i = 0
    for i, _ in enumerate(sphere):
        assert i < len(sphere)

    assert i == 2561


def test_get_item():
    sphere = Points(Points.Geometry.SPHERE)
    p3 = sphere[3]

    assert p3.x == pytest.approx(0.040640)
    assert p3.y == pytest.approx(-0.055937)
    assert p3.z == pytest.approx(0.997607)


def test_get_item_immutable():
    sphere = Points(Points.Geometry.SPHERE)
    sphere[0].x = 1.0
    assert sphere[0].x == 0.0


def test_repr():
    testee = Points(Points.Geometry.ARC)
    assert repr(testee) == '<pyodas2.utils.Points (len=181)>'
