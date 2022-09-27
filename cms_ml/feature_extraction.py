# -*- coding: utf-8 -*-

"""cms_ml.extraction module."""

import logging
import os

import pandas as pd

from cms_ml.utils import filter_values, load_fft_csv

LOGGER = logging.getLogger(__name__)


def aggregate_values(raw_df, name, aggregation, context_fields=True):
    """Aggregates the data values according to the specified aggregation.

    Args:
        raw_df (pd.DataFrame):
            The CMS dataframe to apply the aggregation to.
        name (str):
            Name that will be appended to the signal name.
        aggregation (function):
            The aggregation function to apply.
        context_fields (bool or list):
            If ``bool``, whether or not to return the context columns from the given data.
            If ``list`` parse only the columns specified. Defaults to ``True``.

    Returns:
        pd.DataFrame:
            Contains signal_id, timestamp and value columns. Depending on ``context_fields``
            returns additional columns.
    """
    LOGGER.info('Applying aggregation %s', name)

    output = raw_df.copy()
    if 'values' in output.columns:
        output.rename(columns={'values': 'value'}, inplace=True)

    output["value"] = output["value"].apply(aggregation)
    output["signal_id"] = (output.pop("signal_id").fillna("") + "_" + name).str.strip("_")

    if isinstance(context_fields, list):
        return output[["turbine_id", "signal_id", "timestamp", "value"] + context_fields]

    elif context_fields:
        return output

    return output[["turbine_id", "signal_id", "timestamp", "value"]]


def extract_cms_features(data, aggregations, output_path=None, start_time=None,
                         end_time=None, signals=None, turbines=None, context_fields=True):
    """Extract features from CMS data.

    User function for applying the end-to-end CMS-ML workflow to
    extract cms features from the input data.

    Args:
        data (pandas.DataFrame or str):
            Instance of ``pandas.DataFrame`` or a path to a `csv` file with the accepted format.
        aggregations (dict):
            A dictionary keyed by aggregation function name
            with the function itself as the value.
        output_path (str, optional):
            The path where the csvs will be stored.
        start_time (str, datetime, optional):
            The minimum timestamp, inclusive.
            If None, the timestamps have no minimum. Default is None.
        end_time (str, datetime, optional):
            The maximum timestamp, exclusive.
            If None, the timestamps have no maximum. Default is None.
        signals (list, optional):
            Names of the signals to process.
            If None, all signals in the dataframe are included. Default is None.
        turbines (list, optional):
            The turbines to include in the output. If None, all turbines
            in the dataframe are included. Default is None.
        context_fields (bool or list):
            If ``bool``, whether or not to return the context columns from the given data.
            If ``list`` parse only the columns specified. Defaults to ``True``.

    Returns:
        pd.DataFrame or None:
            The output will have three columns - signal_id, timestamp, value.
            If an output path is provided, return None. The result
            is written to csvs in the output path, per turbine.
            If an output path is not provided and there is only
            one turbine specified, a single dataframe is returned.
            If an output path is not provided and there are multiple turbines
            specified, a dictionary of dataframes keyed by the turbine is returned.
    """

    if (isinstance(data, str) and os.path.isfile(data)):
        data = load_fft_csv(data)

    results = pd.DataFrame()
    data = filter_values(
        data,
        start_time=start_time,
        end_time=end_time,
        signals=signals,
        turbines=turbines,
    )

    for aggregation_name, aggregation in aggregations.items():
        aggregated_df = aggregate_values(
            data,
            aggregation_name,
            aggregation,
            context_fields=context_fields
        )

        results = results.append(aggregated_df, ignore_index=True, sort=False)

    if results['timestamp'].dt.tz:
        results['timestamp'] = results['timestamp'].dt.tz_convert(None)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        LOGGER.info('Writing %s rows to %s', len(results), output_path)
        results.to_csv(output_path, index=False)
    else:
        return results
