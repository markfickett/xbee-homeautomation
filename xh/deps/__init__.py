"""
Verify and import third-party dependencies.
"""

import logging
log = logging.getLogger('xh.deps')

try:
	import serial
except ImportError as e:
	log.error('Required: pySerial >=2.6 '
		+ 'from http://pyserial.sourceforge.net/')
	raise e

try:
	import xbee
except ImportError as e:
	log.error('Required: python-xbee '
		+ 'from http://code.google.com/p/python-xbee/')
	raise e

try:
	from enum import Enum
except ImportError as e:
	log.error('Required: enum from http://pypi.python.org/pypi/enum/')
	raise e
