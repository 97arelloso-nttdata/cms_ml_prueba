import numpy as np


def shift_frequency(amplitude_values, dF, rpm, nominal_rpm, cmstype=None):
    """Shifts the x-axis based on the current rpm versus the nominal.

    Filter between a high and low band and compute the max value for this specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        dF (float):
            The delta frequency (or resolution) of the FFT x-axis.
        rpm (int or float):
            Current RPM from the measurement data.
        nominal_rpm (int or float):
            Nominal RPM for reference.
        cmstype (string):
            type of the cms vibration system.
            different providers have different types of configurations.

    Returns:
        np.ndarray:
            frequency_values corrected for current RPM.
    """
    round_it = True  # this may be introduced as an argument later

    if cmstype == 'tcm':
        fmax = dF * (len(amplitude_values) - 1)
        original_x = np.arange(0, dF + fmax, dF) ## The TCM system includes a frequency value for x = 0
    else:
        original_x = np.arange(dF, dF + len(amplitude_values) * dF, dF)

    if round_it:
        new_x = np.round((original_x * nominal_rpm / rpm) / dF) * dF
    else:
        new_x = original_x * nominal_rpm / rpm

    return new_x
