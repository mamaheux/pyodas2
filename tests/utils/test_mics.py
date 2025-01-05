import pytest

from pyodas2.types import Xyz
from pyodas2.utils import Mic, Mics


def test_init_respeaker_usb_4():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)

    assert len(testee) == 4
    assert testee[0].position.x == pytest.approx(-0.032)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_respeaker_usb_6():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_6)

    assert len(testee) == 6
    assert testee[0].position.x == pytest.approx(-0.0232)
    assert testee[0].position.y == pytest.approx(0.0401)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_minidsp_uma():
    testee = Mics(Mics.Hardware.MINIDSP_UMA)

    assert len(testee) == 7
    assert testee[0].position.x == pytest.approx(0.0)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_sc16_demo_array():
    testee = Mics(Mics.Hardware.SC16_DEMO_ARRAY)

    assert len(testee) == 16
    assert testee[0].position.x == pytest.approx(0.088)
    assert testee[0].position.y == pytest.approx(0.0)
    assert testee[0].position.z == pytest.approx(0.0)


def test_init_sc16f():
    testee = Mics(Mics.Hardware.SC16F)

    assert len(testee) == 16
    assert testee[0].position.x == pytest.approx(-0.0675)
    assert testee[0].position.y == pytest.approx(0.0675)
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


def test_init_uninitialized():
    testee = Mics(16)

    assert len(testee) == 16


def test_init_list():
    testee = Mics([
        Mic(Xyz(1.0, 2.0, 3.0), Xyz(4.0, 5.0, 6.0), Mic.Pattern.OMNIDIRECTIONAL),
        Mic(Xyz(7.0, 8.0, 9.0), Xyz(10.0, 11.0, 12.0), Mic.Pattern.CARDIOID),
    ])

    assert len(testee) == 2

    assert testee[0].position.x == 1.0
    assert testee[0].position.y == 2.0
    assert testee[0].position.z == 3.0
    assert testee[0].direction.x == 4.0
    assert testee[0].direction.y == 5.0
    assert testee[0].direction.z == 6.0
    assert testee[0].pattern == Mic.Pattern.OMNIDIRECTIONAL

    assert testee[1].position.x == 7.0
    assert testee[1].position.y == 8.0
    assert testee[1].position.z == 9.0
    assert testee[1].direction.x == 10.0
    assert testee[1].direction.y == 11.0
    assert testee[1].direction.z == 12.0
    assert testee[1].pattern == Mic.Pattern.CARDIOID


def test_get_item_out_of_range():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)

    with pytest.raises(IndexError):
        _a = testee[5]


def test_get_item_mutable():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee[0].position.x = 10.0
    testee[1].position = Xyz(-10.0, 0.0, 0.0)

    assert testee[0].position.x == 10.0
    assert testee[1].position.x == -10.0

def test_set_item_out_of_range():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)

    with pytest.raises(IndexError):
        testee[5] = Mic(Xyz(1.0, 2.0, 3.0), Xyz(1.0, 2.0, 3.0), Mic.Pattern.CARDIOID)


def test_set_item():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)
    testee[0] = Mic(Xyz(10.0, 0.0, 0.0), Xyz(11.0, 0.0, 0.0), Mic.Pattern.CARDIOID)

    assert testee[0].position.x == 10.0
    assert testee[0].direction.x == 11.0
    assert testee[0].pattern == Mic.Pattern.CARDIOID


def test_repr():
    testee = Mics(Mics.Hardware.RESPEAKER_USB_4)
    assert repr(testee) == '<pyodas2.utils.Mics (len=4)>'
