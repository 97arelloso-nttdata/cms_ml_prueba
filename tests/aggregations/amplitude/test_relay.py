# -*- coding: utf-8 -*-
"""
test for envelope spectrum function
"""
import numpy as np

from cms_ml.aggregations.amplitude.relay import relay_frequency_values

AMPLITUDE_VALUES = np.arange(-10, 15, 0.5)
FREQUENCY_VALUES = np.arange(10, 510, 10)


def test_relay_frequency_values():
    actual = relay_frequency_values(AMPLITUDE_VALUES, FREQUENCY_VALUES)

    np.testing.assert_equal(FREQUENCY_VALUES, actual)
