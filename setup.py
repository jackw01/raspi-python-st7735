from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 3, 0):
    raise RuntimeError("This library requires Python 3.3.0+")

setup(
    name="raspi-python-st7735",
    version="1.0",
    description="Python library for using ST7735-based TFT LCDs with a Raspberry Pi",
    url="https://github.com/jackw01/raspi-python-st7735",
    author="jackw01",
    license="MIT",
    install_requires = [
        'RPi.GPIO>=0.6.2',
        'spidev>=3.0',
        'Pillow>=4.2.0'
    ],
    packages=find_packages()
)
