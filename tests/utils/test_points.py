import pytest

from pyodas2.utils import Points


def test_len():
    sphere = Points(Points.Geometry.SPHERE, 2562)
    assert len(sphere) == 2562

    halfsphere = Points(Points.Geometry.HALFSPHERE, 1321)
    assert len(halfsphere) == 1321

    arc = Points(Points.Geometry.ARC, 181)
    assert len(arc) == 181


def test_get_item_out_of_range():
    sphere = Points(Points.Geometry.SPHERE, 2562)
    i = 0
    for i, _ in enumerate(sphere):
        assert i < len(sphere)

    assert i == 2561


def test_get_item():
    sphere = Points(Points.Geometry.SPHERE, 2562)
    p3 = sphere[3]

    assert p3.x == pytest.approx(0.04494614526629448)
    assert p3.y == pytest.approx(-0.05862433463335037)
    assert p3.z == pytest.approx(0.9972677826881409)


def test_get_item_immutable():
    sphere = Points(Points.Geometry.SPHERE, 2562)
    sphere[0].x = 1.0
    assert sphere[0].x == pytest.approx(0.02793617732822895)


def test_repr():
    testee = Points(Points.Geometry.ARC, 181)
    assert repr(testee) == '<pyodas2.utils.Points (len=181)>'
