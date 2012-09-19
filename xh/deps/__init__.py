"""
Verify and import third-party dependencies.
"""

import logging
import os
import sys


log = logging.getLogger('xh.deps')
SUBMODULE_MSG = 'submodule %s. Try: git submodule update --init'
failedImports = []


def addRelativePath(subdirName, relativeTo):
	"""
	Add a module path (for a dependency) by specifying a path relative to
	some file (typically __file__).
	"""
	sys.path.insert(0, os.path.join(
			os.path.dirname(relativeTo), subdirName))


try:
	name = 'pyserial'
	addRelativePath(name, __file__)
	import serial
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	from enum import Enum
except ImportError as e:
	failedImports.append(('enum from http://pypi.python.org/pypi/enum/', e))

try:
	name = 'pysignals'
	addRelativePath(name, __file__)
	import pysignals
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	name = 'python-xbee'
	addRelativePath(name, __file__)
	import xbee
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

try:
	name = os.path.join('yapsy', 'package')
	addRelativePath(name, __file__)
	import yapsy
except ImportError as e:
	failedImports.append((SUBMODULE_MSG % name, e))

if failedImports:
	msg = 'Unable to import required dependencies:'
	for description, e in failedImports:
		msg += '\n\t%s: requires %s' % (e.message, description)
	log.error(msg)
	raise e

