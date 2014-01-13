#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.3.2'

setup(
    name="tasa",
    version=version,
    description="A simple framework for distributed task workflow using redis.",
    long_description=open("README.rst").read(),
    url='https://github.com/PaulMcMillan/tasa',
    license="Simplified BSD",
    author="Paul McMillan",
    author_email="paul@mcmillan.ws",

    entry_points={
        'console_scripts': [
            'tasa = tasa.cli:run',
            'tasam = tasa.cli:runm',
            'tasa-log = tasa.cli:log',
            ],
        },

    install_requires=[
        "redis",
        ],
    extras_require={
        "tests": [
            "pep8",
            "pylint",
            "pytest",
            "pytest-cov",
            ],
        },
    tests_require=[
        "pep8",
        "pytest",
        "pytest-cov",
        ],

    packages=find_packages(),

    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ])



