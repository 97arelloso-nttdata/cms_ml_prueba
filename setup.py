#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md', encoding='utf-8') as history_file:
    history = history_file.read()

install_requires = [
    'boto3==1.14.44',
    'botocore==1.17.44',
    'matplotlib<3.2.2,>=2.2.2',
    'greenguard>=0.3.0,<0.4',
    'mlprimitives>=0.3.2,<0.4',
    'mlblocks>=0.4.1,<0.5',
    'pandas>=1,<2',
    'sigpro>=0.1.0,<0.2',
    'numpy>=1.17.4,<1.19.0',
]

setup_requires = [
    'pytest-runner>=2.11.1',
]

tests_require = [
    'pytest>=3.4.2',
    'pytest-cov>=2.6.0',
    'jupyter>=1.0.0,<2',
    'rundoc>=0.4.3,<0.5',
]

development_requires = [
    # general
    'pip>=9.0.1',
    'bumpversion>=0.5.3,<0.6',
    'watchdog>=0.8.3,<0.11',

    # docs
    'm2r>=0.2.0,<0.3',
    'nbsphinx>=0.5.0,<0.7',
    'Sphinx>=1.7.1,<3',
    'sphinx_rtd_theme>=0.2.4,<0.5',
    'autodocsumm>=0.1.10',

    # style check
    'flake8>=3.7.7,<4',
    'isort>=4.3.4,<5',

    # fix style issues
    'autoflake>=1.1,<2',
    'autopep8>=1.4.3,<2',

    # distribute on PyPI
    'twine>=1.10.0,<4',
    'wheel>=0.30.0',

    # Advanced testing
    'coverage>=4.5.1,<6',
    'tox>=2.9.1,<4',
    'invoke',

    # Documentation style
    'doc8>=0.8.0,<0.9',
    'pydocstyle>=3.0.0,<4',
]

setup(
    author='MIT Data To AI Lab',
    author_email='dai-lab@mit.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Methods for featurizing CMS data.',
    entry_points={
        'console_scripts': [
            'cms-ml=cms_ml.__main__:main'
        ],
        'mlblocks': [
            'primitives=cms_ml:MLBLOCKS_PRIMITIVES',
            'pipelines=cms_ml:MLBLOCKS_PIPELINES',
        ],
    },
    extras_require={
        'test': tests_require,
        'dev': development_requires + tests_require,
    },
    install_package_data=True,
    install_requires=install_requires,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='cms-ml CMS Machine Learning',
    name='cms-ml',
    packages=find_packages(include=['cms_ml', 'cms_ml.*']),
    python_requires='>=3.6,<3.9',
    setup_requires=setup_requires,
    test_suite='tests',
    tests_require=tests_require,
    url='https://github.com/sintel-dev/CMS-ML',
    version='0.1.7.dev1',
    zip_safe=False,
)
