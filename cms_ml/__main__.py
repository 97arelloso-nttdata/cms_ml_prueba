#!/usr/bin/env python
# coding: utf-8

import argparse
import logging

import numpy as np

from cms_ml import extract_cms_context, extract_cms_features

LOGGER = logging.getLogger(__name__)


def _raw(values):
    return values


def _rms(values):
    return np.sqrt((np.array(values) ** 2).mean())


AGGREGATIONS = {
    'std': np.std,
    'mean': np.mean,
    'rms': _rms,
    'raw': _raw
}


def logging_setup(verbosity=1, logfile=None, logger_name=None):
    logger = logging.getLogger(logger_name)
    log_level = (3 - verbosity) * 10
    fmt = '%(asctime)s - %(process)d - %(levelname)s - %(module)s - %(message)s'
    formatter = logging.Formatter(fmt)
    logger.setLevel(log_level)
    logger.propagate = False

    if logfile:
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def _extract_cms_features(args):
    aggregations = {
        name: AGGREGATIONS[name]
        for name in args.aggregation
    }
    signals = args.signals.split(',') if args.signals else None
    turbines = args.turbines.split(',') if args.turbines else None

    LOGGER.info('Extracting CMS Features:')
    LOGGER.info('    Input: %s', args.input)
    LOGGER.info('    Output: %s', args.output)
    LOGGER.info('    Aggregations: %s', args.aggregation)

    if signals:
        LOGGER.info('    Signals: %s', args.signals)
    if turbines:
        LOGGER.info('    Turbines: %s', args.signals)
    if args.start_time:
        LOGGER.info('    Start Time: %s', args.start_time)
    if args.end_time:
        LOGGER.info('    End Time: %s', args.end_time)

    extract_cms_features(aggregations, args.input, args.output, args.start_time,
                         args.end_time, signals, turbines)


def _extract_cms_context(args):
    signals = args.signals.split(',') if args.signals else None
    turbines = args.turbines.split(',') if args.turbines else None

    LOGGER.info('Extracting CMS Context:')
    LOGGER.info('    Input: %s', args.input)
    LOGGER.info('    Output: %s', args.output)

    if args.fields:
        LOGGER.info('    Fields: %s', args.fields)
    if signals:
        LOGGER.info('    Signals: %s', args.signals)
    if turbines:
        LOGGER.info('    Turbines: %s', args.signals)
    if args.start_time:
        LOGGER.info('    Start Time: %s', args.start_time)
    if args.end_time:
        LOGGER.info('    End Time: %s', args.end_time)

    extract_cms_context(args.input, args.output, args.fields, args.start_time,
                        args.end_time, signals, turbines)


def get_parser():
    """
    $ cms-ml extract_cms_features -i /path/to/jsons/folder \
                                             -o /path/to/output/csvs/folder \
                                             -a rms \
                                             -s 2010-01-01 \
                                             -e 2011-01-01 \
                                             -S S1,S2,S3 \
                                             -T T1,T2
    """

    # Common Parent - Shared options
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument('-l', '--logfile',
                      help='Name of the logfile. If not given, log to stdout.')
    base.add_argument('-v', '--verbose', action='count', default=0,
                      help='Be verbose. Use -vv for increased verbosity.')

    common = argparse.ArgumentParser(add_help=False, parents=[base])
    common.add_argument('-i', '--input', help='Input JSONS path')
    common.add_argument('-o', '--output', help='Output CSVs path')
    common.add_argument('-s', '--start-time', required=False, help='Minimum tiemstamp to extract')
    common.add_argument('-e', '--end-time', required=False, help='Maximum tiemstamp to extract')
    common.add_argument('-S', '--signals', required=False,
                        help='Comma separated list of Signal ids')
    common.add_argument('-T', '--turbines', required=False,
                        help='Comma separated list of Turbine ids')

    parser = argparse.ArgumentParser(description='CMS-ML Command Line Interface.')
    parser.set_defaults(function=None)

    action = parser.add_subparsers(title='action', dest='action')
    action.required = True

    features = action.add_parser('features', help='Extract aggregated feautres', parents=[common])
    features.set_defaults(function=_extract_cms_features)
    features.add_argument('-a', '--aggregation', action='append',
                          choices=list(AGGREGATIONS.keys()), required=True,
                          help='Aggregation to apply. Can be used multiple times.')

    context = action.add_parser('context', help='Extract context values', parents=[common])
    context.set_defaults(function=_extract_cms_context)
    context.add_argument('-f', '--fields',
                         help='Comma separated list of fields to extract. If skipped, extract all')

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    logging_setup(args.verbose, args.logfile)

    args.function(args)
