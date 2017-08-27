#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alexey Sintsov'

from setuptools import setup

setup(
    name='CANToolz',
    version='3.6.1',
    description='Framework for black-box Controller Area Network (CAN) bus analysis.',
    author='Alexey Sintsov',
    author_email='alex.sintsov@gmail.com',
    license='Apache 2.0',
    keywords='framework black-box CAN analysis security',
    packages=['cantoolz', 'cantoolz.stream', 'cantoolz.utils', 'cantoolz.modules'],
    url='https://github.com/CANToolz/CANToolz',
    install_requires=[
        'pyserial',
        'mido',
        'numpy',
        'bitstring'
    ],
)
