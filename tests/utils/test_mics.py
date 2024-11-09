import pytest

from pyodas2.utils import Mics, Mic
from pyodas2.types import Xyz


def test_init_respeaker_usb():
    testee = Mics(Mics.Hardware.RESPEAKER_USB)

    assert len(testee) == 4
    assert testee[0].position.x == pytest.approx(-0.032)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_minidsp_uma():
    testee = Mics(Mics.Hardware.MINIDSP_UMA)

    assert len(testee) == 7
    assert testee[0].position.x == pytest.approx(0.0)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_introlab_circular():
    testee = Mics(Mics.Hardware.INTROLAB_CIRCULAR)

    assert len(testee) == 4
    assert testee[0].position.x == pytest.approx(0.088)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_vibeus_circular():
    testee = Mics(Mics.Hardware.VIBEUS_CIRCULAR)

    assert len(testee) == 6
    assert testee[0].position.x == pytest.approx(-0.045)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_soundskrit_mug():
    testee = Mics(Mics.Hardware.SOUNDSKRIT_MUG)

    assert len(testee) == 3
    assert testee[0].position.x == pytest.approx(0.03750)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_get_item_out_of_range():
    testee = Mics(Mics.Hardware.RESPEAKER_USB)

    with pytest.raises(IndexError):
        a = testee[5]


def test_get_item_mutable():
    testee = Mics(Mics.Hardware.RESPEAKER_USB)
    testee[0].position.x = 10.0
    testee[1].position = Xyz(-10.0, 0.0, 0.0)

    assert testee[0].position.x == 10.0
    assert testee[1].position.x == -10.0

def test_set_item_out_of_range():
    testee = Mics(Mics.Hardware.RESPEAKER_USB)

    with pytest.raises(IndexError):
        testee[5] = Mic(Xyz(1.0, 2.0, 3.0), Xyz(1.0, 2.0, 3.0), Mic.Pattern.CARDIOID)


def test_set_item():
    testee = Mics(Mics.Hardware.RESPEAKER_USB)
    testee[0] = Mic(Xyz(10.0, 0.0, 0.0), Xyz(11.0, 0.0, 0.0), Mic.Pattern.CARDIOID)

    assert testee[0].position.x == 10.0
    assert testee[0].direction.x == 11.0
    assert testee[0].pattern == Mic.Pattern.CARDIOID
