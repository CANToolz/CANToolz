from distutils.core import setup

setup(
    name='CANToolz',
    version='3.1.0',
    author='Alexey Sintsov',
    author_email='alex.sintsov@gmail.com',
    packages=['cantoolz', 'cantoolz.stream', 'cantoolz.utils', 'cantoolz.modules'],
    scripts=[],
    url='https://github.com/eik00d/CANToolz',
    license='Apache 2.0',
    description='Framework and library for black-box analysis and reverse engineering of Controller Area Network (CAN)',
    long_description=open('README.md').read(),

)