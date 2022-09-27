import json
import logging
import os

import pandas as pd

LOGGER = logging.getLogger(__name__)


def get_cms_values(entry):
    """Parse a CMS JSON entry into a pd.Series containing the CMS values.

    Args:
        entry (dict):
            A raw JSON entry containing CMS data.

    Returns:
        pd.DataFrame:
            Containing name,timeStamp,yValues extracted from the entry.
    """
    data = entry['data']
    details = entry['details']
    datasets = data['set']

    length = len(datasets)
    if length == 1:
        suffixes = ('',)
    elif length == 2:
        suffixes = ('X', 'Y')
    else:
        raise ValueError('More than 2 datasets found')

    result = []
    for dataset, suffix in zip(datasets, suffixes):
        result.append({
            'signal_id': '_'.join([details['sensorName'], details['name'], suffix]).strip('_'),
            'timestamp': data['context']['timeStamp'],
            'values': dataset['yValues']
        })

    result = pd.DataFrame(result)
    result['timestamp'] = pd.to_datetime(result['timestamp'])

    return result


def get_cms_context(entry, fields=None):
    """Parse a CMS JSON entry into a pd.Series containing the desired CMS context.

    Args:
        entry (dict):
            A raw JSON entry containing CMS data.
        fields (list, None, optional):
            CMS context fields to select for. If None, return all
            context fields (every field except yValues). Default is None.

    Returns:
        pd.DataFrame:
            Containing context values extracted from the entry.
    """
    row = entry['details'].copy()
    row.update(entry['location'])
    data = entry['data']
    context = data['context'].copy()
    for key in ['extra', 'binningParameters', 'operationalValues']:
        values = context.pop(key, list())
        for value in values:
            context[value['name']] = value['value']

    row.update(context)

    row['name'] = "_".join([row['sensorName'], row['name']])

    dataset = data['set']

    dataset = dataset[0].copy()
    del dataset["yValues"]
    row.update(dataset)

    output = pd.DataFrame([row])
    output.insert(0, 'timestamp', pd.to_datetime(output.pop('timeStamp')))
    output.insert(0, 'signal_id', output.pop('name'))
    if fields is not None:
        if 'signal_id' in fields:
            fields.remove('signal_id')
        if 'timestamp' in fields:
            fields.remove('timestamp')

        output = output[['signal_id', 'timestamp'] + fields]

    return output


def parse_cms_jsons(jsons_path, parser, *args, **kwargs):
    """Parses json files into a dataframe.

    Extracts the JSON file(s) from the file path, parses them using the
    inputted parser, and converts the data into a dataframe.

    Args:
        jsons_path (str):
            The file path to a folder containing the jsons for one turbine.
        parser (function):
            Function used to parse a JSON entry into a pandas Series.
            An example is get_cms_context.
        *args, **kwargs:
            Additional args and kwargs to pass to the parser function.

    Returns:
        pd.DataFrame:
            Contains the data parsed from the JSON file(s).
    """
    parsed = pd.DataFrame()
    LOGGER.info('Parsing JSON files from folder %s', jsons_path)
    for filename in os.listdir(jsons_path):
        json_file = os.path.join(jsons_path, filename)

        LOGGER.debug('Parsing JSON file %s', json_file)
        with open(json_file) as f:
            for entry in json.load(f):
                parsed_entry = parser(entry, *args, **kwargs)
                parsed = parsed.append(parsed_entry, ignore_index=True, sort=False)

    LOGGER.info('%s entries loaded', len(parsed))
    return parsed


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
