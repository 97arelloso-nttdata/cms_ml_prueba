from configparser import RawConfigParser, ConfigParser
from cms_ml.parsers.cms_med_classes import MEDData
import pandas as pd
import os
import re
import numpy as np
from io import StringIO
from datetime import datetime as dt
import glob


# TODO: Add a column renaming dictionary. Default none.

def parse_adu_cms_txt(filedir, out=None, renamer=None):
    """
    Parses txt file containing "adu format" CMS data into a dataframe
    :param filedir: route to the file to be parsed
    :param out: if not None, out should be a valid directory into which the dataframe will be output as a CSV file.
    Invalid directories will raise an Error.
    :param renamer: dict containing new names for the columns of the output dataframe.
    :return: pd.DataFrame containing the parsed information
    """
    filename = filedir.split('\\')[-1].split('/')[-1].split('.txt')[0]

    # Check output directory
    if out is not None:
        path_exists = os.path.isdir(out)
        if not path_exists:
            raise Exception('{} is not a valid existing path'.format(out))
        file_exists = os.path.isfile(os.path.join(out, '.'.join([filename, 'csv'])))
        if file_exists:
            raise Exception('File with name {}.csv already exists in given path'.format(filename))

    with open(filedir, 'r') as file:
        end_process_token = '#--finish--'
        state = 0
        ini_io = StringIO()
        data_array = dict()
        cur_data = ''
        adu_chan = ''
        raw_data = dict()
        for line in file.readlines():
            if state == 0:
                if re.findall('^\[.*prescanopc.*\]$', line) and not re.findall('^\[.*data.*\]$', line):
                    cur_data = line.split('[')[1].split(']')[0]
                if re.findall('^\[.*aduchannel.*\]$', line):
                    adu_chan = line.split('[')[1].split(']')[0]
                if re.findall('^\[.*data.*\]$', line) and not re.findall('^\[.*adudata.*\]$', line):
                    state = 1
                    data_array.update({cur_data: StringIO()})
                    continue
                if re.findall('^\[.*adudata.*\]$', line):
                    state = 2
                    raw_data.update({adu_chan: StringIO()})
                ini_io.write(line)
            elif state == 1:
                if line.strip() == end_process_token:
                    ini_io.write(line)
                    state = 0
                    continue
                data_array[cur_data].write(line.split()[1]+'\n')
            elif state == 2:
                if line.strip() == end_process_token:
                    ini_io.write(line)
                    state = 0
                    continue
                raw_data[adu_chan].write(line)
            else:
                ini_io.write(line)
        file.close()

    ini_io.seek(0)
    config_parser = RawConfigParser()
    config_parser.read_file(ini_io)

    out_df = pd.DataFrame()
    metrics = dict()
    for k, el in data_array.items():
        el.seek(0)
        p = el.getvalue()
        metadata = {i: config_parser[k][i] for i in config_parser[k]}
        p = np.array(p.split('\n')[:-1]).astype('float64')
        mean = p.mean()
        maximum = np.max(p)
        minimum = np.min(p)
        std = p.std()
        starttime = dt.fromtimestamp(int(metadata['starttime']))
        label = metadata['szlabel']
        row = {label+'_mean': mean,
               label+'_min': minimum,
               label+'_max': maximum,
               label+'_std': std,
               'timestamp': starttime}
        metrics.update(row)

    for k, v in raw_data.items():
        v.seek(0)
        p = v.getvalue()
        p = np.array(p.split('\n')[:-1]).astype('float64')
        metrics.update({'values': p})
    out_df = out_df.append([metrics])

    if renamer is not None:
        aux = dict()
        for k, v in renamer.items():
            if k in out_df.columns:
                aux.update({k: v})
        out_df.rename(columns=aux, inplace=True)
    if out is not None:
        out_df.to_csv(os.path.join(out, '.'.join([filename, 'csv'])), header=True, index=False)

    return out_df


def parse_med_txt(filedir, turbine_id='', rms=True, out=None, renamer=None):
    """

    :param filedir: route to the file to be parsed
    :param turbine_id: id of the turbine to be parsed. If not specified, it will be retrieved from the .MED file
    :param rms: if true, adds rms data as raw lists to the dataframe. Otherwise, it skips it
    :param out: if not None, it should be a valid directory to which the dataframe is output as a csv
    :param renamer: dict containing new names for the columns of the output dataframe.
    :return:
    """
    filename = filedir.split('\\')[-1].split('/')[-1].split('.med')[0]
    # Check output directory
    if out is not None:
        path_exists = os.path.isdir(out)
        if not path_exists:
            raise Exception('{} is not a valid existing path'.format(out))
        file_exists = os.path.isfile(os.path.join(out, '.'.join([filename, 'csv'])))
        if file_exists:
            raise Exception('File with name {}.csv already exists in given path'.format(filename))

    parser = MEDData(filedir, filename=filename)
    if turbine_id:
        parser.set_turbine(turbine=turbine_id)
    parsed = parser.to_dataframe(rms=rms)

    if renamer is not None:
        aux = dict()
        for k, v in renamer.items():
            if k in parsed.columns:
                aux.update({k: v})
        parsed.rename(columns=aux, inplace=True)

    if out is not None:
        parsed.to_csv(os.path.join(out, '.'.join([filename, 'csv'])), header=True, index=False)

    return parsed


def parse_cms_txt(filedir, out=None, renamer=None):
    """
    Parses txt file containing CMS data into a dataframe
    :param filedir: route to the file to be parsed
    :param out: if not None, out should be a valid directory into which the dataframe will be output as a CSV file.
    Invalid directories will raise an Error.
    :param renamer: dict containing new names for the columns of the output dataframe.
    :return: pd.DataFrame containing the parsed information
    """
    filename = filedir.split('\\')[-1].split('/')[-1].split('.txt')[0]

    # Check output directory
    if out is not None:
        path_exists = os.path.isdir(out)
        if not path_exists:
            raise Exception('{} is not a valid existing path'.format(out))
        file_exists = os.path.isfile(os.path.join(out, '.'.join([filename, 'csv'])))
        if file_exists:
            raise Exception('File with name {}.csv already exists in given path'.format(filename))

    with open(filedir, 'r') as file:
        end_process_token = '#--finish--'
        state = 0
        ini_io = StringIO()
        data_array = dict()
        cur_data = ''
        for line in file.readlines():
            if state == 0:
                if re.findall('^\[.*specchannel.*\]$', line):
                    cur_data = line.split('[')[1].split(']')[0]
                if re.findall('^\[.*specdata.*\]$', line):
                    state = 1
                    data_array.update({cur_data: StringIO()})
                    continue
                ini_io.write(line)
            elif state == 1:
                if line.strip() == end_process_token:
                    ini_io.write(line)
                    state = 0
                    continue
                data_array[cur_data].write(line)
            else:
                ini_io.write(line)
        file.close()

    ini_io.seek(0)
    config_parser = RawConfigParser()
    config_parser.read_file(ini_io)

    out_df = pd.DataFrame()

    for k, el in data_array.items():
        el.seek(0)
        p = el.getvalue()
        p = np.array(p.split('\n')[:-1]).astype('float64')
        metadata = dict()
        # We try converting all numeric fields in metadata to float. If it fails it means the field is not numerical
        # and therefore we don't need to convert it
        for i in config_parser[k]:
            try:
                cast_type = float(config_parser[k][i])
            except:
                cast_type = config_parser[k][i]

            metadata.update({i, cast_type})

        dic = dict()
        dic['turbine_id'] = metadata['szsystemid']
        dic['signal_id'] = '_'.join([metadata['szlabel'], metadata['ianalysisid'], k])
        dic['timestamp'] = dt.fromtimestamp(int(metadata['starttime']))
        dic.update({'values': p})
        metadata.pop('szsystemid')
        metadata.pop('szlabel')
        metadata.pop('ianalysisid', '')
        metadata.pop('starttime')
        dic.update(metadata)
        out_df = out_df.append([dic])

    if renamer is not None:
        aux = dict()
        for k, v in renamer.items():
            if k in out_df.columns:
                aux.update({k: v})
        out_df.rename(columns=aux, inplace=True)
    if out is not None:
        out_df.to_csv(os.path.join(out, '.'.join([filename, 'csv'])), header=True, index=False)

    return out_df


def parse_cms_directory(input_directory, parser, substring='', extension = 'txt', renamer=None, out=None, out_filename=None):
    """

    :param input_directory: Directory through which the method will iterate
    :param parser: parser function to execute
    :param substring: Substring to look for on filenames for further filtering
    :param renamer: dict containing new names for the columns of the output dataframe.
    :param out: Optional output directory for dataframe.
    :param out_filename: Optional filename for the output dataframe. Requires out to be not None. If given an output
    directory but not a filename, the output filename will default to "parser_output.csv"
    :return: pd.DataFrame
    """
    # Check output directory
    if out is not None:
        if out_filename is None:
            out_filename = 'parser_output'
        path_exists = os.path.isdir(out)
        if not path_exists:
            raise Exception('{} is not a valid existing path'.format(out))
        file_exists = os.path.isfile(os.path.join(out, '.'.join([out_filename, 'csv'])))
        if file_exists:
            raise Exception('File with name {}.csv already exists in given path'.format(out_filename))

    path_exists = os.path.isdir(input_directory)
    if not path_exists:
        raise Exception('{} is not a valid existing path'.format(input_directory))

    out_df = pd.DataFrame()

    for el in glob.glob(os.path.join(input_directory, '*{0}*.{1}'.format(substring, extension))):
        out_df = out_df.append(parser(el, renamer=renamer))

    if out is not None:
        out_df.to_csv(os.path.join(out, '.'.join([out_filename, 'csv'])), header=True, index=False)
    return out_df


