# -*- coding: utf-8 -*-
"""
test for envelope spectrum function
"""
import numpy as np

from cms_ml.aggregations.amplitude.band import (
    band_max, band_mean, band_min, band_rms, band_sideband_pr, band_sideband_rms)

AMPLITUDE_VALUES = np.arange(-10, 15, 0.5)
FREQUENCY_VALUES = np.arange(10, 510, 10)


def test_band_mean():
    expected = 2.0
    actual = band_mean(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=100, max_frequency=400)

    assert actual == expected


def test_band_max():
    expected = -5.5
    actual = band_max(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=30, max_frequency=100)

    assert expected == actual


def test_band_min():
    expected = -9.0
    actual = band_min(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=30, max_frequency=100)

    assert expected == actual


def test_band_rms():
    expected = 4.8648398398
    actual = band_rms(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=30, max_frequency=350)

    np.testing.assert_almost_equal(actual, expected)


def test_band_sideband_rms():
    expected = 8.2202413846
    actual = band_sideband_rms(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=30,
                               max_frequency=100, side_bands=[(400, 500), (10, 30), (200, 350)])

    np.testing.assert_almost_equal(actual, expected)


def test_band_sideband_pr():
    expected = 1.149800749
    actual = band_sideband_pr(AMPLITUDE_VALUES, FREQUENCY_VALUES, min_frequency=30,
                              max_frequency=100, side_bands=[(400, 500), (10, 30), (200, 350)])

    np.testing.assert_almost_equal(actual, expected)
