"""
Verify and import third-party dependencies.
"""

import logging
import os
import sys


log = logging.getLogger('xh.deps')
SUBMODULE_MSG = 'submodule %s. Try: git submodule update --init'
failedImports = []

def _addLocalPath(subdirName):
	sys.path.append(os.path.join(os.path.dirname(__file__), subdirName))

try:
	import serial
except ImportError as e:
	failedImports.append(
		('pySerial >=2.6 from http://pyserial.sourceforge.net/', e))

try:
	from enum import Enum
except ImportError as e:
	failedImports.append(('enum from http://pypi.python.org/pypi/enum/', e))

try:
	import yapsy
except ImportError as e:
	failedImports.append(
		('yapsy from http://sourceforge.net/projects/yapsy/', e))

try:
	name = 'pysignals'
	addLocalPath(name)
	import pysignals
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	name = 'python-xbee'
	addLocalPath(name)
	import xbee
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

if failedImports:
	msg = 'Unable to import required dependencies:'
	for description, e in failedImports:
		msg += '\n\t%s: requires %s' % (e.message, description)
	log.error(msg)
	raise e

