#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for cms_ml package."""
from unittest import TestCase
from unittest.mock import call, patch

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

from cms_ml.demo import get_demo_data
from cms_ml.feature_extraction import aggregate_values, extract_cms_features


class TestAggregateValues(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.DataFrame(
            {
                'signal_id': ['Signal_1', 'Signal_1', 'Signal_2'],
                'timestamp': ['2019-10-19T13:27:18+00:00', '2019-11-19T13:27:18+00:00',
                              '2019-12-19T13:27:18+00:00'],
                'value': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            })

    @classmethod
    def rms(self, data):
        return np.sqrt((np.array(data) ** 2).mean())

    @classmethod
    def mean(self, data):
        return np.array(data).mean()

    def test_aggregate_values_rms(self):
        expected = pd.DataFrame(
            {
                'timestamp': ['2019-10-19T13:27:18+00:00', '2019-11-19T13:27:18+00:00',
                              '2019-12-19T13:27:18+00:00'],
                'value': [2.160247, 5.066228, 8.041559],
                'signal_id': ['Signal_1_rms', 'Signal_1_rms', 'Signal_2_rms'],
            })
        actual = aggregate_values(self.data, "rms", self.rms)
        assert_frame_equal(expected, actual)

    def test_aggregate_values_mean(self):
        expected = pd.DataFrame(
            {
                'timestamp': ['2019-10-19T13:27:18+00:00', '2019-11-19T13:27:18+00:00',
                              '2019-12-19T13:27:18+00:00'],
                'value': [2.0, 5.0, 8.0],
                'signal_id': ['Signal_1_mean', 'Signal_1_mean', 'Signal_2_mean'],
            })
        actual = aggregate_values(self.data, "mean", self.mean)
        assert_frame_equal(expected, actual)

    def test_aggregate_values_error(self):
        with pytest.raises(KeyError):
            aggregate_values(pd.DataFrame({'name': [],
                                           'timeStamp': [],
                                           'yValues': []}), "mean", self.mean)


class TestFeatureExtractCMSFeatures(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = get_demo_data()
        cls.data = cls.data.head(5)

    @patch('cms_ml.feature_extraction.aggregate_values')
    @patch('cms_ml.feature_extraction.filter_values')
    def test_extract_cms_features(self, filter_mock, agg_mock):

        # setup
        agg_mock.side_effect = [
            pd.DataFrame({
                'turbine_id': ['T001', 'T001'],
                'signal_id': ['signal_1_mean', 'signal_2_mean'],
                'timestamp': pd.to_datetime(['2000-01-10', '2000-01-10'], utc=True),
                'values': [1, 2]
            }),
            pd.DataFrame({
                'turbine_id': ['T001', 'T001'],
                'signal_id': ['signal_1_std', 'signal_2_std'],
                'timestamp': pd.to_datetime(['2000-01-10', '2000-01-10'], utc=True),
                'values': [3, 4]
            }),
        ]

        aggregations = {
            'mean': np.mean,
            'std': np.std
        }

        # run
        result = extract_cms_features(
            self.data,
            aggregations,
            start_time='2000-01-01',
            end_time='2000-02-01',
            signals=['signal_1', 'signal_2']
        )

        # assert
        expected = pd.DataFrame({
            'turbine_id': ['T001', 'T001', 'T001', 'T001'],
            'signal_id': ['signal_1_mean', 'signal_2_mean', 'signal_1_std', 'signal_2_std'],
            'timestamp': pd.to_datetime(['2000-01-10', '2000-01-10', '2000-01-10', '2000-01-10']),
            'values': [1, 2, 3, 4],
        })
        pd.testing.assert_frame_equal(expected, result)

        filter_mock.assert_called_once_with(
            self.data,
            start_time='2000-01-01',
            end_time='2000-02-01',
            signals=['signal_1', 'signal_2'],
            turbines=None
        )

        exp_agg_calls = [
            call(filter_mock.return_value, 'mean', np.mean, context_fields=True),
            call(filter_mock.return_value, 'std', np.std, context_fields=True),
        ]
        assert agg_mock.call_args_list == exp_agg_calls

    @patch('pandas.DataFrame.to_csv')
    @patch('cms_ml.feature_extraction.aggregate_values')
    @patch('cms_ml.feature_extraction.filter_values')
    def test_extract_cms_context_output_path(self, filter_mock, agg_mock, to_csv_mock):
        # setup
        agg_mock.side_effect = [
            pd.DataFrame({
                'turbine_id': ['T001', 'T001'],
                'signal_id': ['signal_1_mean', 'signal_2_mean'],
                'timestamp': pd.to_datetime(['2000-01-10', '2000-01-10'], utc=True),
                'values': [1, 2]
            }),
            pd.DataFrame({
                'turbine_id': ['T001', 'T001'],
                'signal_id': ['signal_1_std', 'signal_2_std'],
                'timestamp': pd.to_datetime(['2000-01-10', '2000-01-10'], utc=True),
                'values': [3, 4]
            }),
        ]

        aggregations = {
            'mean': np.mean,
            'std': np.std
        }

        # run
        result = extract_cms_features(
            self.data,
            aggregations,
            start_time='2000-01-01',
            end_time='2000-02-01',
            signals=['signal_1', 'signal_2'],
            output_path='path/to/output.csv'
        )

        # assert
        filter_mock.assert_called_once_with(
            self.data,
            start_time='2000-01-01',
            end_time='2000-02-01',
            signals=['signal_1', 'signal_2'],
            turbines=None
        )

        exp_agg_calls = [
            call(filter_mock.return_value, 'mean', np.mean, context_fields=True),
            call(filter_mock.return_value, 'std', np.std, context_fields=True),
        ]
        assert agg_mock.call_args_list == exp_agg_calls

        assert result is None

        to_csv_mock.assert_called_once_with('path/to/output.csv', index=False)
