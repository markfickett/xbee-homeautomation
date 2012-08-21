"""
Verify and import third-party dependencies.
"""

import logging, os, sys
log = logging.getLogger('xh.deps')

failedImports = []

try:
	import serial
except ImportError as e:
	failedImports.append(
		('pySerial >=2.6 from http://pyserial.sourceforge.net/', e))

try:
	import xbee
except ImportError as e:
	failedImports.append(
		('python-xbee from http://code.google.com/p/python-xbee/', e))

try:
	from enum import Enum
except ImportError as e:
	failedImports.append(('enum from http://pypi.python.org/pypi/enum/', e))

try:
	import yapsy
except ImportError as e:
	failedImports.append(
		('yapsy from http://sourceforge.net/projects/yapsy/', e))

if failedImports:
	msg = 'Unable to import required dependencies:'
	for description, e in failedImports:
		msg += '\n\t%s: requires %s' % (e.message, description)
	log.error(msg)
	raise e

PYSIGNALS_PATH = os.path.join(os.path.dirname(__file__), 'pysignals')
sys.path.append(PYSIGNALS_PATH)
import pysignals

