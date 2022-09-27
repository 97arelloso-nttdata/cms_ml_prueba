# -*- coding: utf-8 -*-
"""
test for envelope spectrum function
"""
import numpy as np

from cms_ml.transformations.amplitude.order_track import shift_frequency

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
DELTA_FREQUENCY = 0.5
RPM = 995
NOMINAL_RPM = 1000


def test_shift_frequency():
    # setup
    expected_amplitude = np.array([
        0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5,
        6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0,
        11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5,
        17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0,
        22.5, 23.0, 23.5, 24.0, 24.5, 25.0
    ])

    # run
    result_amplitude = shift_frequency(AMPLITUDE_VALUES,
                                       DELTA_FREQUENCY,
                                       RPM,
                                       NOMINAL_RPM)

    # assert
    np.testing.assert_array_equal(result_amplitude, expected_amplitude)


def test_shift_frequency_cmstype():
    # setup
    expected_amplitude = np.array([
        0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5,
        6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0,
        11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5,
        17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0,
        22.5, 23.0, 23.5, 24.0, 24.5
    ])

    # run
    result_amplitude = shift_frequency(AMPLITUDE_VALUES,
                                       DELTA_FREQUENCY,
                                       RPM,
                                       NOMINAL_RPM,
                                       cmstype='tcm')

    # assert
    np.testing.assert_array_equal(result_amplitude, expected_amplitude)
