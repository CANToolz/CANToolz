from setuptools import setup
import pip
import sys

if len(sys.argv) >= 2 and sys.argv[1] == 'install':
    #pip.main(['install', 'neurolab'])
    pip.main(['install', 'pyserial'])
    pip.main(['install', 'numpy'])
    pip.main(['install', 'mido'])
    #pip.main(['install', 'scipy'])
    #pip.main(['install', 'pybrain'])
    pip.main(['install', 'bitstring'])


setup(
    name='CANToolz',
    version='3.6.0',
    author='Alexey Sintsov',
    install_requires=[
        'pyserial',
        'mido',
        'numpy','bitstring'
    ],
    author_email='alex.sintsov@gmail.com',
    packages=['cantoolz', 'cantoolz.stream', 'cantoolz.utils', 'cantoolz.modules'],
    scripts=[],
    url='https://github.com/eik00d/CANToolz',
    license='Apache 2.0',
    description='Framework and library for black-box analysis and reverse engineering of Controller Area Network (CAN)'


)