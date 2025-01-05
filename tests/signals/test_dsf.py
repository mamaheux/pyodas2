import math

import pytest

from pyodas2.signals import Dsf


def test_init_too_long_label():
    Dsf('1' * 63)

    with pytest.raises(ValueError, match='The label is too long. The maximum length is 63.'):
        Dsf('1' * 64)

def test_init():
    testee = Dsf('dsf')

    assert testee.label == 'dsf'
    assert math.isclose(testee.sigmoid_mean, 0.3, abs_tol=1e-3)
    assert math.isclose(testee.sigmoid_slope, 40.0, abs_tol=1e-3)
    assert math.isclose(testee.tracked_source_sigma2, 0.05, abs_tol=1e-3)
    assert math.isclose(testee.tracked_source_threshold, 0.25, abs_tol=1e-3)
    assert math.isclose(testee.tracked_source_rate, 0.1, abs_tol=1e-3)
    assert math.isclose(testee.new_source_sigma2, 0.01, abs_tol=1e-3)
    assert math.isclose(testee.new_threshold, 0.4, abs_tol=1e-3)
    assert math.isclose(testee.delete_threshold, 0.2, abs_tol=1e-3)
    assert math.isclose(testee.delete_decay, 0.98, abs_tol=1e-3)
