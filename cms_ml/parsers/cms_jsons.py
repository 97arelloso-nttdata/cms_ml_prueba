import gc
import json
import logging
import os

import pandas as pd

from cms_ml.utils import filter_values

LOGGER = logging.getLogger(__name__)


def _get_cms_values(entry):
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


def _get_cms_context(entry, fields=None):
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


def _parse_cms_jsons(jsons_path, parser, *args, **kwargs):
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


def extract_cms_jsons(jsons_path, output_path=None, start_time=None,
                      end_time=None, signals=None, turbines=None, context_fields=True):
    """Extract CMS data from JSONS.

    User function that loads and extracts FFT timeseries from JSON files.

    Args:
        jsons_path (str):
            The file path to the directory with turbines folders
            containing JSON files.
        output_path (str, optional):
            The path where the csvs will be stored.
        start_time (str, datetime, optional):
            The minimum timestamp, inclusive.
            If None, the timestamps have no minimum. Default is None.
        end_time (str, datetime, optional):
            The maximum timestamp, exclusive.
            If None, the timestamps have no maximum. Default is None.
        turbines (list, optional):
            The turbines to include in the output. If None, all turbines
            in the extracted dataframe are included. Default is None.
        signals (list, optional):
            Names of the signals to process. If None,
            all signals in the extracted data are included. Default is None.
        context_fields (bool or list):
            If ``bool`` whether or not to parse the context columns from the jsons. If ` `list``
            parse only the given list of fields from the context. Defaults to ``True``.

    Returns:
        pd.DataFrame or None:
            If an output path is provided, return None. The result
            is written to csvs in the output path, per turbine.
            If an output path is not provided and there is only
            one turbine specified, a single dataframe is returned.
            If an output path is not provided and there are multiple turbines
            specified, a dictionary of dataframes keyed by the turbine is returned.
    """
    # traversing the directories
    results = pd.DataFrame()
    for name in os.listdir(jsons_path):
        path = os.path.join(jsons_path, name)
        if os.path.isdir(path) and ((not turbines) or (name in turbines)):
            gc.collect()
            data = _parse_cms_jsons(path, _get_cms_values)
            if context_fields:
                parsed_context = _parse_cms_jsons(path, _get_cms_context)
                if isinstance(context_fields, list):
                    parsed_context = parsed_context[[context_fields]]

                data = parsed_context.merge(data)

            filtered = filter_values(
                data, start_time=start_time, end_time=end_time, signals=signals)

            filtered.insert(0, 'turbine_id', name)
            results = results.append(filtered, ignore_index=True, sort=False)

    if results['timestamp'].dt.tz:
        results['timestamp'] = results['timestamp'].dt.tz_convert(None)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        LOGGER.info('Writing %s rows to %s', len(results), output_path)
        results.to_csv(output_path, index=False)
    else:
        return results
