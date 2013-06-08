#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.1.1'

setup(
    name="tasa",
    version=version,
    description="A simple job queue framework using redis.",
    long_description=open("README.md").read(),
    url='https://github.com/PaulMcMillan/tasa',
    license="Simplified BSD",
    author="Paul McMillan",
    author_email="paul@mcmillan.ws",

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

    packages=find_packages(exclude=['tests', 'examples']),

    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ])



