#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for cms_ml.parsing."""
from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, call, patch

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

from cms_ml.parsers.cms_jsons import (
    _get_cms_context, _get_cms_values, _parse_cms_jsons, filter_values)


class TestCMSParseEntry(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = {'details': {'name': 'Signal_1', 'sensorName': 'Sensor_1'},
                     'location': {'turbineName': 'T001-93'},
                     'data': {'context': {'timeStamp': '2019-11-19T13:27:18+00:00',
                                          'extra': [{'name': 'Mask Status', 'value': ''}],
                                          'binningParameters': [{'name': 'WPS-ActivePower-Average',
                                                                 'value': '1733.3'}],
                                          'operationalValues': [{'name': 'Measured RPM',
                                                                 'value': 1451.202}],
                                          'condition': 'WPS-ActivePower 1657-1909'},
                              'set': [{'yValueUnit': '1', 'yValues': [1, 2, 3]}]}}

    def test__get_cms_values(self):
        returned = _get_cms_values(self.entry)

        expected = pd.DataFrame([{
            'signal_id': 'Sensor_1_Signal_1',
            'timestamp': pd.to_datetime('2019-11-19T13:27:18+00:00'),
            'values': [1, 2, 3]
        }])
        assert_frame_equal(expected, returned)

    def test_get_cms_value_XY(self):
        current_entry = deepcopy(self.entry)
        current_entry['data']['set'] = [{'yValueUnit': '1', 'yValues': [4, 5, 6]},
                                        {'yValueUnit': '1', 'yValues': [1, 2, 3]}]
        returned = _get_cms_values(current_entry)
        expected = pd.DataFrame([
            {
                'signal_id': 'Sensor_1_Signal_1_X',
                'timestamp': pd.to_datetime('2019-11-19T13:27:18+00:00'),
                'values': [4, 5, 6]
            },
            {
                'signal_id': 'Sensor_1_Signal_1_Y',
                'timestamp': pd.to_datetime('2019-11-19T13:27:18+00:00'),
                'values': [1, 2, 3]
            }
        ])
        assert_frame_equal(expected, returned)

    def test__get_cms_context_default(self):
        returned = _get_cms_context(self.entry)

        expected = pd.DataFrame([{
            'signal_id': 'Sensor_1_Signal_1',
            'sensorName': 'Sensor_1',
            'turbineName': 'T001-93',
            'timestamp': pd.to_datetime('2019-11-19T13:27:18+00:00'),
            'condition': 'WPS-ActivePower 1657-1909',
            'Mask Status': '',
            'WPS-ActivePower-Average': '1733.3',
            'Measured RPM': 1451.202,
            'yValueUnit': '1'
        }])
        assert_frame_equal(expected, returned, check_like=True)

    def test__get_cms_context_fields(self):
        fields = ["signal_id", "turbineName", "timestamp",
                  "WPS-ActivePower-Average"]
        expected = pd.DataFrame([{
            'signal_id': 'Sensor_1_Signal_1',
            'turbineName': 'T001-93',
            'timestamp': pd.to_datetime('2019-11-19T13:27:18+00:00'),
            'WPS-ActivePower-Average': '1733.3'
        }])
        returned = _get_cms_context(self.entry, fields)
        assert_frame_equal(expected, returned, check_like=True)


class TestParseCMSJsons(TestCase):
    @patch('cms_ml.parsers.cms_jsons.json')
    @patch('cms_ml.parsers.cms_jsons.open')
    @patch('cms_ml.parsers.cms_jsons.os.listdir')
    def test__parse_cms_jsons_single_file_value(self, listdir_mock, open_mock, json_mock):
        # setup
        listdir_mock.return_value = ['a.json']
        json_mock.load.return_value = [{'a': 'json'}]
        parser = Mock()
        parser.return_value = pd.DataFrame([{
            'signal_id': 'a_json',
            'timestamp': 'a_timestamp',
            'value': [1, 2, 3]
        }])

        # run
        returned = _parse_cms_jsons('a/jsons/path', parser)

        # asserts
        expected_return = pd.DataFrame([{
            'signal_id': 'a_json',
            'timestamp': 'a_timestamp',
            'value': [1, 2, 3]
        }])
        pd.testing.assert_frame_equal(expected_return, returned)

        listdir_mock.assert_called_once_with('a/jsons/path')

        open_mock.assert_called_once_with('a/jsons/path/a.json')

        parser.called_once_with({'a': 'json'})

    @patch('cms_ml.parsers.cms_jsons.json')
    @patch('cms_ml.parsers.cms_jsons.open')
    @patch('cms_ml.parsers.cms_jsons.os.listdir')
    def test__parse_cms_jsons_multiple_value(self, listdir_mock, open_mock, json_mock):
        # setup
        listdir_mock.return_value = ['a.json', 'another.json']
        json_mock.load.side_effect = [
            [{
                'a': 'json'
            }],
            [{
                'another': 'json'
            }],
        ]
        parser = Mock()
        parser.side_effect = [
            pd.DataFrame([{
                'signal_id': 'a_json',
                'timestamp': 'a_timestamp',
                'value': [1, 2, 3]
            }]),
            pd.DataFrame([{
                'signal_id': 'another_json',
                'timestamp': 'another_timestamp',
                'value': [4, 5, 6]
            }]),
        ]

        # run
        returned = _parse_cms_jsons('a/jsons/path', parser)

        # asserts
        expected_return = pd.DataFrame({
            'signal_id': ['a_json', 'another_json'],
            'timestamp': ['a_timestamp', 'another_timestamp'],
            'value': [[1, 2, 3], [4, 5, 6]]
        })

        assert_frame_equal(expected_return, returned)

        listdir_mock.assert_called_once_with('a/jsons/path')

        open_calls = [
            call('a/jsons/path/a.json'),
            call('a/jsons/path/another.json')
        ]
        self.assertListEqual(open_calls, open_mock.call_args_list)

        parser_calls = [
            call({'a': 'json'}),
            call({'another': 'json'}),
        ]
        self.assertListEqual(parser_calls, parser.call_args_list)

    @patch('cms_ml.parsers.cms_jsons.json')
    @patch('cms_ml.parsers.cms_jsons.open')
    @patch('cms_ml.parsers.cms_jsons.os.listdir')
    def test__parse_cms_jsons_multiple_value_XY(self, listdir_mock, open_mock, json_mock):
        # setup
        listdir_mock.return_value = ['a.json', 'another.json']
        json_mock.load.side_effect = [
            [{
                'a': 'json'
            }],
            [{
                'another': 'json'
            }],
        ]
        parser = Mock()
        parser.side_effect = [
            pd.DataFrame([{
                'signal_id': 'a_json',
                'timestamp': 'a_timestamp',
                'value': [1, 2, 3]
            }]),
            pd.DataFrame([{
                'signal_id': 'another_json',
                'timestamp': 'another_timestamp',
                'value': [4, 5, 6]},
                {
                'signal_id': 'another_json',
                'timestamp': 'another_timestamp',
                'value': [7, 8, 9]}]),
        ]

        # run
        returned = _parse_cms_jsons('a/jsons/path', parser)

        # asserts
        expected_return = pd.DataFrame({
            'signal_id': ['a_json', 'another_json', 'another_json'],
            'timestamp': ['a_timestamp', 'another_timestamp', 'another_timestamp'],
            'value': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        })

        assert_frame_equal(expected_return, returned)

        listdir_mock.assert_called_once_with('a/jsons/path')

        open_calls = [
            call('a/jsons/path/a.json'),
            call('a/jsons/path/another.json')
        ]
        self.assertListEqual(open_calls, open_mock.call_args_list)

        parser_calls = [
            call({'a': 'json'}),
            call({'another': 'json'}),
        ]
        self.assertListEqual(parser_calls, parser.call_args_list)

    @patch('cms_ml.parsers.cms_jsons.json')
    @patch('cms_ml.parsers.cms_jsons.open')
    @patch('cms_ml.parsers.cms_jsons.os.listdir')
    def test__parse_cms_jsons_multiple_context(self, listdir_mock, open_mock, json_mock):
        # setup
        listdir_mock.return_value = ['a.json', 'another.json']
        json_mock.load.side_effect = [
            [{
                'a': 'json'
            }],
            [{
                'another': 'json'
            }],
        ]
        parser = Mock()
        parser.side_effect = [
            pd.DataFrame([{
                'signal_id': 'Signal_1',
                'turbineName': 'T001-93',
                'timestamp': 'a_timestamp',
                'condition': 'WPS-ActivePower 1657-1909',
                'Mask Status': '',
                'WPS-ActivePower-Average': '1733.3',
                'Measured RPM': 1451.202,
                'yValueUnit': '1'
            }]),
            pd.DataFrame([{
                'signal_id': 'Signal_1',
                'turbineName': 'T001-93',
                'timestamp': 'another_timestamp',
                'condition': 'WPS-ActivePower 1657-1909',
                'WPS-ActivePower-Average': '1900',
                'Measured RPM': 1200.1,
                'yValueUnit': '1'
            }]),
        ]

        # run
        returned = _parse_cms_jsons('a/jsons/path', parser)

        # asserts
        expected_return = pd.DataFrame(
            {
                'signal_id': ['Signal_1', 'Signal_1'],
                'turbineName': ['T001-93', 'T001-93'],
                'timestamp': ['a_timestamp', 'another_timestamp'],
                'condition': ['WPS-ActivePower 1657-1909', 'WPS-ActivePower 1657-1909'],
                'Mask Status': ['', np.nan],
                'WPS-ActivePower-Average': ['1733.3', '1900'],
                'Measured RPM': [1451.202, 1200.1],
                'yValueUnit': ['1', '1']
            })

        assert_frame_equal(expected_return, returned, check_like=True)

        listdir_mock.assert_called_once_with('a/jsons/path')

        open_calls = [
            call('a/jsons/path/a.json'),
            call('a/jsons/path/another.json')
        ]
        self.assertListEqual(open_calls, open_mock.call_args_list)

        parser_calls = [
            call({'a': 'json'}),
            call({'another': 'json'}),
        ]
        self.assertListEqual(parser_calls, parser.call_args_list)


class TestFilterValues(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.DataFrame(
            {
                'signal_id': ['Signal_1', 'Signal_1', 'Signal_2'],
                'timestamp': ['2019-10-19T13:27:18+00:00', '2019-11-19T13:27:18+00:00',
                              '2019-12-19T13:27:18+00:00'],
                'value': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            })
        cls.expected_1 = pd.DataFrame(
            {
                'signal_id': ['Signal_1', 'Signal_1'],
                'timestamp': ['2019-10-19T13:27:18+00:00', '2019-11-19T13:27:18+00:00'],
                'value': [[1, 2, 3], [4, 5, 6]],
            })

    def test_filter_values_no_args(self):
        returned = filter_values(self.data)
        assert_frame_equal(self.data, returned)

    def test_filter_values_date_strings(self):
        actual = filter_values(self.data, start_time="2019-10-01", end_time="2019-12-01")
        assert_frame_equal(self.expected_1, actual)

    def test_invalid_string(self):
        with pytest.raises(ValueError):
            filter_values(self.data, start_time="INVALID", end_time="2019-12-01")

    def test_filter_values_datetimes(self):
        actual = filter_values(self.data, start_time=datetime(2019, 10, 1),
                               end_time=datetime(2019, 12, 1))
        assert_frame_equal(self.expected_1, actual)

    def test_filter_values_signals(self):
        expected_2 = pd.DataFrame(
            {
                'signal_id': ['Signal_2'],
                'timestamp': ['2019-12-19T13:27:18+00:00'],
                'value': [[7, 8, 9]],
            })
        actual_1 = filter_values(self.data, signals=["Signal_1"])
        assert_frame_equal(self.expected_1, actual_1)
        actual_2 = filter_values(self.data, signals=["Signal_2"]).reset_index(drop=True)
        assert_frame_equal(expected_2, actual_2)
        actual_3 = filter_values(self.data, signals=["Signal_1", "Signal_2"])
        assert_frame_equal(actual_3, self.data)

    def test_filter_values_all(self):
        actual = filter_values(self.data, start_time="2019-10-01",
                               end_time="2019-12-01", signals=["Signal_1"])
        assert_frame_equal(self.expected_1, actual)
