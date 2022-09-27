# coding: utf-8

import io
import json
import os
import random
import re
import shutil
import urllib
import zipfile

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.signal import stft

from cms_ml.utils import load_fft_csv

DEMO_PATH = os.path.join(os.path.dirname(__file__), 'data')


def _download_data():
    """Download original data used to build the CMS-ML Demo.

    Original source: https://www.researchgate.net/publication/303792317_Experimental_Dataset_for_Gear_Fault_Diagnosis
    """  # noqa

    url = 'https://drive.google.com/uc?id=0B4vlQFEs8N-cT3djQmwtV2NWSjg&export=download'
    response = urllib.request.urlopen(url)
    bio = io.BytesIO(response.read())

    data = dict()
    re_name = re.compile(r'Gearbox_(\w*)_full_load_\w*_10kHz_pos1.mat')
    with zipfile.ZipFile(bio) as zf:
        for name in zf.namelist():
            if re_name.match(name):
                key = re_name.sub(r'\1', name)
                with io.BytesIO(zf.read(name)) as bio:
                    data[key] = sio.loadmat(bio)['acc'].ravel()

    return data


def _extract_data(data, apply_fft=False):
    """Extract fft values from vibration timeseries data.

    The fft transformation is applied on intervals of 400 data points
    and only the real part of them is returned.

    Args:
        apply_fft (bool):
            Whether or not to apply fft transformation to the timeseries data.

    Returns:
        Return signal values, if ``apply_fft`` is ``True`` then ``fft`` transform will
        be applyed to those.
    """
    all_data = dict()
    for name, values in data.items():
        data = list()
        all_data[name] = data
        for i in range(250):
            start = i * 400
            end = (i + 1) * 400
            ts = values[start:end]
            if apply_fft:
                ts = np.real(np.fft.fft(ts))

            data.append(ts)

    return all_data


def build_demo(apply_fft=False):
    """Generate a CMS-ML demo from the gearbox data.

    The demo is based on the experimental dataset obtained by the ``_dowload_data``
    method and simulates the following scenario:

    1. At the begining everything was fine
    2. After 251 hours a tooth got chipped
    3. After 501 hours three teeth were worn out

    This method returns the corresponding target_times and values DataFrames. If
    ``apply_fft`` is ``True``, apply fft to the timeseries.

    Args:
        apply_fft (bool):
            Whether or not to apply fft transformation to the timeseries data.

    Returns:
        A ``tuple`` containing two `pd.DataFrame` with the target times and the timeseries,
        if ``apply_fft`` is ``True`` the timeseries will contain FFT values of the signal.
    """
    data = _download_data()
    ffts = _extract_data(data, apply_fft)
    df = pd.DataFrame({
        'turbine_id': 'T001',
        'signal_id': 'Sensor1_signal1',
        'timestamp': pd.date_range(start='2020-01-01', periods=750, freq='1h'),
        'values': ffts['no_fault'] + ffts['a_chipped_tooth'] + ffts['three_worn_teeth'],
        'target': ['no_fault'] * 250 + ['a_chipped_tooth'] * 250 + ['three_worn_teeth'] * 250
    })
    target_times = df[['turbine_id', 'timestamp', 'target']].sample(50).copy()
    target_times = target_times.rename(columns={'timestamp': 'cutoff_time'})

    values = df[['turbine_id', 'signal_id', 'timestamp', 'values']].copy()

    return target_times, values


def _make_jsons(values):
    """Generate a list of CMS-like dictionaries from the given values."""
    jsons = list()
    for _, row in values.iterrows():
        fft_values = list(row['values'])
        freqs = np.fft.fftfreq(len(fft_values))
        offset = freqs[0]
        delta = freqs[1] - offset
        sensor, signal = row.signal_id.split('_')

        jsons.append({
            "data": {
                "context": {
                    "timeStamp": row.timestamp.isoformat(),
                },
                "set": [
                    {
                        "xValueDelta": delta,
                        "yValues": fft_values,
                        "xValueOffset": offset,
                        "xValueUnit": "Hz",
                        "yValueUnit": "1"
                    }
                ]
            },
            "details": {
                "name": signal,
                "sensorName": sensor,
            },
            "location": {
                "turbineName": row.turbine_id,
            }
        })

    return jsons


def make_demo_jsons(path='data', force=False):
    """Load a dataframe with FFT timeseries and convert it in to accepted json format."""
    if os.path.exists(path):
        if force:
            shutil.rmtree(path)
        else:
            msg = 'Path "{}" already exists. Please remove it or use `force=True`'.format(path)
            raise FileExistsError(msg)

    output_path = os.path.join(path, 'T001')
    os.makedirs(output_path, exist_ok=True)

    # export_path = os.path.join(DEMO_PATH, 'T001')
    demo_fft_path = os.path.join(DEMO_PATH, 'demo_fft_timeseries.csv')

    df = load_fft_csv(demo_fft_path)
    jsons = _make_jsons(df)

    output_path = os.path.join(output_path, 'data.json')
    with open(output_path, 'w') as jsons_file:
        json.dump(jsons, jsons_file)


def get_demo_data(fft=False):
    """Get a demo ``pandas.DataFrame`` containing the accepted data format.

    Args:
        fft (bool):
            Whether or not to apply fft transformation to the timeseries data.

    Returns:
        A ``pd.DataFrame`` containing as ``values`` the signal values. If ``fft`` is
        ``True`` the values will contain the values after applying ``fft`` transformation.

    """
    if fft:
        demo_path = os.path.join(DEMO_PATH, 'demo_fft_timeseries.csv')
    else:
        demo_path = os.path.join(DEMO_PATH, 'demo_timeseries.csv')

    return load_fft_csv(demo_path)


def get_amplitude_demo(idx=None):
    """Get amplitude values and sampling frequency used.

    The amplitude demo data is meant to be used for the any ``transformation`` functions
    that recieve as an input ``amplitude_values`` and ``sampling_frequency``.

    This amplitude values are loaded from the demo data without any transformations
    being applied to those values. There are `750` different signals. You can specify
    the desired index in order to retrive the same signal over and over, otherwise it
    will return a random signal.

    Args:
        idx (int or None):
            If `int`, return the value at that index if `None` return a random index.

    Returns:
        tuple:
            A tuple with a `np.array` containing amplitude values and as second element the
            sampling frequency used.
    """
    df = get_demo_data(fft=False)
    if idx is None:
        idx = random.randint(0, len(df))

    return np.array(df.iloc[idx]['values']), 10000


def get_frequency_demo(idx=None):
    """Get amplitude values and the corresponding frequency values.

    The frequency demo data is meant to be used for the ``frequency aggregations``
    functions that recieve as an input ``amplitude_values`` and ``frequency_values``.

    This amplitude values are loaded from the demo data with ``fft`` transformations
    being applied to those values. There are `750` different signals. You can specify
    the desired index in order to retrive the same signal over and over, otherwise it
    will return a random signal.

    Args:
        idx (int or None):
            If `int`, return the value at that index if `None` return a random index.

    Returns:
        tuple:
            A tuple two `np.array` containing amplitude values and frequency values.
    """
    amplitude_values, sampling_frequency = get_amplitude_demo(idx)
    fft_values = np.fft.fft(amplitude_values)
    frequencies = np.fft.fftfreq(len(fft_values), sampling_frequency)
    return fft_values, frequencies


def get_frequency_time_demo(idx=None):
    """Get amplitude values, frequency values and time values.

    The frequency time demo data is meant to be used for the ``frequency time aggregations``
    functions that recieve as an input ``amplitude_values``, ``frequency_values`` and
    ``time_values``.

    This amplitude values are loaded from the demo data with ``fft`` transformations
    being applied to those values then a ``stft`` is being computed. There are `750`
    different signals. You can specify the desired index in order to retrive the same
    signal over and over, otherwise it will return a random signal.

    Args:
        idx (int or None):
            If `int`, return the value at that index if `None` return a random index.

    Returns:
        tuple:
            A tuple two `np.array` containing amplitude values and frequency values.
    """
    amplitude_values, sampling_frequency = get_amplitude_demo(idx)
    sample_frequencies, time_values, amplitude_values = stft(
        amplitude_values,
        fs=sampling_frequency
    )

    return amplitude_values, sample_frequencies, time_values


def get_demo_target_times():
    """Get a demo ``pandas.DataFrame`` containing target times."""
    demo_tt_path = os.path.join(DEMO_PATH, 'demo_target_times.csv')
    return pd.read_csv(demo_tt_path, parse_dates=['cutoff_time'])
