import json
import logging

import pandas as pd

LOGGER = logging.getLogger(__name__)


def load_fft_csv(path):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    df["values"] = df["values"].apply(json.loads).apply(list)
    return df


def filter_values(raw_df, start_time=None, end_time=None, signals=None, turbines=None):
    """Filters the dataframe based on timestamp and signal.

    The timestamp of a row must be within the specified time range
    and be a signal within the selected signals.

    Args:
        raw_df (pd.DataFrame):
            The CMS dataframe to filter.
        start_time (str, datetime, optional):
            The minimum timestamp, inclusive.
            If None, the timestamps have no minimum. Default is None.
        end_time (str, datetime, optional):
            The maximum timestamp, exclusive.
            If None, the timestamps have no maximum. Default is None.
        signals (list, optional):
            Names of the signals to process. If None,
            all signals in the extracted data are included. Default is None.
        turbines (list, optional):
            Names of the turbines to process. If None,
            all turbines in the extracted data are included. Default is None.
    Returns:
        pd.DataFrame:
            Values filtered as specified above.
    """
    timestamps = pd.to_datetime(raw_df['timestamp'])
    if timestamps.dt.tz:
        timestamps = timestamps.dt.tz_convert(None)

    mask = [True] * len(raw_df)
    if start_time:
        LOGGER.info('Filtering by start time %s', start_time)
        start_time = pd.to_datetime(start_time)
        if start_time.tz:
            start_time = start_time.tz_convert(None)

        mask &= timestamps >= start_time

    if end_time:
        LOGGER.info('Filtering by end time %s', end_time)
        end_time = pd.to_datetime(end_time)
        if end_time.tz:
            end_time = end_time.tz_convert(None)

        mask &= timestamps < end_time

    if signals:
        LOGGER.info('Filtering by signals %s', signals)
        mask &= raw_df['signal_id'].str.contains('|'.join(signals), na=False, case=False)

    if turbines:
        LOGGER.info('Filtering by turbines %s', turbines)
        mask &= raw_df['turbine_id'].str.contains('|'.join(turbines), na=False, case=False)

    final_df = raw_df[mask]
    LOGGER.info('Selected %s entries after filtering', len(final_df))

    return final_df
