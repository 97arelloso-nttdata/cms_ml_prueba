# -*- coding: utf-8 -*-
"""CMS-ML Transformations Frequency Envelopespectrum module."""
import numpy as np
from scipy.fftpack import fft
from scipy.signal import butter, hilbert, lfilter


def _butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def _butter_bandpass_filter(data, fs, lowcut, highcut, order=5):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def envelopespectrum(amplitude_values, sampling_frequency, lowcut=None, highcut=None, order=5):
    """
    Envelope spectrum for machinery diagnosis

    Computes the envelope spectrum, envspectrum, of the 'amplitude_values'.
    'amplitude_values' is sampled at a rate of 'sampling_frequency'.
    envelopespectrum contains the one-sided magnitude spectrum
    of the envelope signal of 'amplitude_values'.

    envelopespectrum has (N/2+1) rows if N, the length of amplitude_values, is even,
    and (N+1)/2 rows if N is odd.

    Args:
        amplitude_values (np.ndarray):
           A numpy array with the signal values.
        sampling_frequency (int or float):
           Sampling frequency value passed in Hz.
        lowcut (float):
           lower end of frequency band where envelope spectrum is computed , defaults to `None`.
        highcut (float):
           higher end of frequency band where envelope spectrum is computed, defaults to `None`.
        order (int):
           FIR filter order, positive integer defaults to 5.
    """

    data = amplitude_values
    fs = sampling_frequency
    if lowcut is None or lowcut > fs / 2:
        lowcut = fs / 4
    if highcut is None or highcut >= fs / 2:
        highcut = fs * 3 / 8

    filtered = _butter_bandpass_filter(data, fs, lowcut, highcut, order=order)
    analytic_signal = hilbert(filtered)
    amplitude_envelope = np.abs(analytic_signal)
    envelope_DCRemoved = amplitude_envelope - amplitude_envelope.mean()
    env_fft = fft(envelope_DCRemoved)
    N = len(env_fft)
    xf = np.linspace(0, float(fs) / (2), N // 2)
    envspectrum = 2.0 / N * np.abs(env_fft[0:N // 2])

    return envspectrum, xf
