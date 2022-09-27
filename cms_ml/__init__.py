# -*- coding: utf-8 -*-

"""Top-level package for CMS-ML."""

__author__ = 'MIT Data To AI Lab'
__email__ = 'dai-lab@mit.edu'
__version__ = '0.1.7.dev1'

import os

from mlblocks import discovery

from cms_ml.demo import get_demo_data, get_demo_target_times, make_demo_jsons
from cms_ml.feature_extraction import extract_cms_features

_BASE_PATH = os.path.abspath(os.path.dirname(__file__))
MLBLOCKS_PRIMITIVES = os.path.join(_BASE_PATH, 'primitives')
MLBLOCKS_PIPELINES = os.path.join(_BASE_PATH, 'pipelines')

__all__ = (
    'get_demo_data',
    'get_demo_target_times',
    'make_demo_jsons',
    'extract_cms_features',
)


def get_pipelines(pipeline_type=None):
    """Get a list of the available pipelines.

    Optionally filter by pipeline type: ``cms_fe`` or ``cms_ml``.

    Args:
        pipeline_type (str):
            Filter by pipeline type. ``cms_fe`` or ``cms_ml``.

    Returns:
        list:
            List of the names of the available pipelines.
    """
    if pipeline_type and pipeline_type not in ('cms_ml', 'cms_fe'):
        raise ValueError('pipeline_type must be `cms_ml` or `cms_fe`')

    return discovery.find_pipelines(pipeline_type or 'cms')
