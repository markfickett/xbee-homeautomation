"""
Centralized imports and module setup.
"""

import logging
logging.basicConfig(
        format='[%(levelname)s %(name)s] %(message)s',
        level=logging.DEBUG)
import sys, os, time
import optparse

try:
	import serial
except ImportError, e:
	'Required: pySerial >=2.6 from http://pyserial.sourceforge.net/'
	raise e
try:
	import xbee
except ImportError, e:
	'Required: python-xbee from http://code.google.com/p/python-xbee/'
	raise e

try:
	from enum import Enum
except ImportError, e:
	'Required: enum from http://pypi.python.org/pypi/enum/'
	raise e

import Config, Encoding, Protocol
