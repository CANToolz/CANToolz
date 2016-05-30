from setuptools import setup
import pip
import sys

if len(sys.argv) >= 2 and sys.argv[1] == 'install':
    pip.main(['install', 'pyserial'])
    pip.main(['install', 'numpy'])
    pip.main(['install', 'mido'])


setup(
    name='CANToolz',
    version='3.3.3',
    author='Alexey Sintsov',
    install_requires=[
        'pyserial',
        'mido',
        'numpy'
    ],
    author_email='alex.sintsov@gmail.com',
    packages=['cantoolz', 'cantoolz.stream', 'cantoolz.utils', 'cantoolz.modules'],
    scripts=[],
    url='https://github.com/eik00d/CANToolz',
    license='Apache 2.0',
    description='Framework and library for black-box analysis and reverse engineering of Controller Area Network (CAN)'


)