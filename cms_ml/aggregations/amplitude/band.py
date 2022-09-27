import numpy as np


def _in_range(frequency_values, min_frequency, max_frequency):
    lower_frequency_than = frequency_values <= max_frequency
    higher_frequency_than = frequency_values >= min_frequency
    return np.ravel(higher_frequency_than & lower_frequency_than)


def _filter_side_bands(frequency_values, side_bands):
    side_bands_idx = np.array([])

    for side_band in side_bands:
        min_sb, max_sb = side_band
        low_f = frequency_values <= max_sb
        high_f = frequency_values >= min_sb
        sb_idx = np.where(low_f & high_f)
        side_bands_idx = np.concatenate((side_bands_idx, sb_idx), axis=None)

    return side_bands_idx


def band_mean(amplitude_values, frequency_values, min_frequency, max_frequency):
    """Compute the mean values for a specific band.

    Filter between a high and low band (inclusive) and compute the mean value for this specific
    band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.

    Returns:
        float:
            Mean value for the given band.
    """
    selected_idx = np.ravel(np.where(_in_range(frequency_values, min_frequency, max_frequency)))

    selected_idx = [int(x) for x in selected_idx]

    selected_values = np.array(amplitude_values)[selected_idx]

    return np.mean(selected_values)


def band_max(amplitude_values, frequency_values, min_frequency, max_frequency):
    """Compute the max values for a specific band.

    Filter between a high and low band (inclusive) and compute the max value for this
    specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.

    Returns:
        float:
            Max value for the given band.
    """
    selected_idx = np.ravel(np.where(_in_range(frequency_values, min_frequency, max_frequency)))

    selected_idx = [int(x) for x in selected_idx]

    selected_values = np.array(amplitude_values)[selected_idx]

    return np.max(selected_values)


def band_min(amplitude_values, frequency_values, min_frequency, max_frequency):
    """Compute the min values for a specific band.

    Filter between a high and low band (inclusive) and compute the min value for this
    specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.

    Returns:
        float:
            Min value for the given band.
    """
    selected_idx = np.ravel(np.where(_in_range(frequency_values, min_frequency, max_frequency)))

    selected_idx = [int(x) for x in selected_idx]

    selected_values = np.array(amplitude_values)[selected_idx]

    return np.min(selected_values)


def band_rms(amplitude_values, frequency_values, min_frequency, max_frequency):
    """Compute the rms values for a specific band.

    Filter between a high and low band (inclusive) and compute the rms value for this
    specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.

    Returns:
        float:
            rms value for the given band.
    """
    selected_idx = np.ravel(np.where(_in_range(frequency_values, min_frequency, max_frequency)))

    selected_idx = [int(x) for x in selected_idx]

    selected_values = np.array(amplitude_values)[selected_idx]

    return np.sqrt(np.mean(np.square(selected_values)))


def band_sideband_rms(amplitude_values,
                      frequency_values,
                      min_frequency,
                      max_frequency,
                      side_bands):
    """Compute the rms values for a specific band and associated sidebands.

    Filter between a high and low band (inclusive) and compute
    the mean value for this specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.
        side_bands (list of tuples (sideband_min (int or float), sideband_max (int or float))):
            List of tuples with the sideband minium and maximum.
    Returns:
        float:
            RMS value for the given band and associated sidebands.
    """
    selected_idx = np.where(_in_range(frequency_values, min_frequency, max_frequency))
    side_bands_idx = _filter_side_bands(frequency_values, side_bands)

    final_idx = np.concatenate((selected_idx, side_bands_idx), axis=None)  # <-

    selected_values = np.array(amplitude_values)[final_idx.astype(dtype="int")]
    return np.sqrt(np.mean(np.square(selected_values)))


def band_sideband_pr(amplitude_values, frequency_values,
                     min_frequency, max_frequency, side_bands):
    """Compute the power ratio values for side bands vs a specific band.

    Filter between a high and low band (inclusive) and compute
    the mean value for this specific band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.
        side_bands (list of tuples (sideband_min (int or float), sideband_max (int or float))):
            List of tuples with the sideband minium and maximum.
    Returns:
        float:
            Power ratio value for side bands vs a specific band.
    """
    selected_idx = np.where(_in_range(frequency_values, min_frequency, max_frequency))
    selected_values = np.array(amplitude_values)[selected_idx]

    band_rms = np.sqrt(np.mean(np.square(selected_values)))

    side_bands_idx = _filter_side_bands(frequency_values, side_bands)

    selected_values = np.array(amplitude_values)[side_bands_idx.astype(dtype="int")]
    side_band_rms = np.sqrt(np.mean(np.square(selected_values)))

    return side_band_rms / band_rms

def band_sum(amplitude_values, frequency_values, min_frequency, max_frequency):
    """Compute the sum values for a specific band.

    Filter between a high and low band (inclusive) and compute the sum value for this specific
    band.

    Args:
        amplitude_values (np.ndarray):
            A numpy array with the signal values.
        frequency_values (np.ndarray):
            A numpy array with the frequency values.
        min_frequency (int or float):
            Band minimum.
        max_frequency (int or float):
            Band maximum.

    Returns:
        float:
            Sum value for the given band.
    """
    selected_idx = np.ravel(np.where(_in_range(frequency_values, min_frequency, max_frequency)))

    selected_idx = [int(x) for x in selected_idx]

    selected_values = np.array(amplitude_values)[selected_idx]

    return np.sum(selected_values)