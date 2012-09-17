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
	sys.path.insert(0, os.path.join(os.path.dirname(__file__), subdirName))

try:
	name = 'pyserial'
	_addLocalPath(name)
	import serial
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	from enum import Enum
except ImportError as e:
	failedImports.append(('enum from http://pypi.python.org/pypi/enum/', e))

try:
	name = 'pysignals'
	_addLocalPath(name)
	import pysignals
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	name = 'python-xbee'
	_addLocalPath(name)
	import xbee
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	name = 'yapsy/package'
	_addLocalPath(name)
	import yapsy
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

if failedImports:
	msg = 'Unable to import required dependencies:'
	for description, e in failedImports:
		msg += '\n\t%s: requires %s' % (e.message, description)
	log.error(msg)
	raise e

