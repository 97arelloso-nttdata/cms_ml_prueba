# -*- coding: utf-8 -*-
"""
test for envelope spectrum function
"""
import numpy as np

from cms_ml.transformations.frequency.envelopespectrum import envelopespectrum

AMPLITUDE_VALUES = np.array([
    0.03170188, 0.0102072, -0.00879151, 0.04678361, 0.05459194,
    0.03229712, 0.06062183, 0.08041962, 0.07629004, 0.08775747,
    0.10005213, 0.1084305, 0.11923816, 0.12503383, 0.13367566,
    0.14547279, 0.15169235, 0.1584296, 0.16788527, 0.17513588,
    0.18164428, 0.18884732, 0.19551726, 0.20172567, 0.20773555,
    0.21344134, 0.21883227, 0.22391439, 0.22868642, 0.23314797,
    0.23729953, 0.24114247, 0.24467899, 0.24791212, 0.25084568,
    0.25348423, 0.25583309, 0.25789823, 0.25968628, 0.26120449,
    0.26246067, 0.26346312, 0.26422064, 0.26474244, 0.26503811,
    0.26511756, 0.26499096, 0.26466873, 0.26416144, 0.26347979
])
SAMPLING_FREQUENCY = 10000


def test_envelopespectrum():
    # setup
    expected_amplitude = np.array([
        1.00613962e-18, 7.69441638e-03, 4.90059180e-03, 3.26258504e-03,
        1.93535752e-03, 1.02606905e-03, 7.28021434e-04, 3.25361501e-04,
        2.16390640e-04, 1.71153649e-04, 1.71528844e-04, 1.55822220e-04,
        1.30942947e-04, 6.92939327e-05, 6.23673674e-05, 6.83444693e-05,
        5.77132724e-05, 5.32852013e-05, 4.58306013e-05, 2.54339110e-05,
        3.32340408e-05, 3.13919272e-05, 2.64941869e-05, 2.69892099e-05,
        2.24700386e-05
    ])
    expected_frequency = np.array([
        0., 208.33333333, 416.66666667, 625.,
        833.33333333, 1041.66666667, 1250., 1458.33333333,
        1666.66666667, 1875., 2083.33333333, 2291.66666667,
        2500., 2708.33333333, 2916.66666667, 3125.,
        3333.33333333, 3541.66666667, 3750., 3958.33333333,
        4166.66666667, 4375., 4583.33333333, 4791.66666667,
        5000.
    ])

    # run
    result_amplitude, result_frequency = envelopespectrum(AMPLITUDE_VALUES, SAMPLING_FREQUENCY)

    # assert
    np.testing.assert_array_almost_equal(result_amplitude, expected_amplitude)
    np.testing.assert_array_almost_equal(result_frequency, expected_frequency)