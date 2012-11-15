"""
Read a local graph configuration file.

A graph configuration file defines a number of Python dicts which describe how
to rename, dice up, and otherwise transform log data -- typically (time, volts)
pairs -- into various named lines on various graphs. The config structure is
somewhat informed by Dygraphs's options and native data structure (see 
http://dygraphs.com/).

An minimal example:

fahrenheit = {
	'title': 'Temperature (F)',
	'map': tmp36VoltsToF,
	'series': {
		'0x0013a20082fab0-AD0': [{'title': 'Outside'}],
	}
}

Comprehensively:

# The special name 'html' is inserted at the beginning of the generated page's
# body verbatim.
html = "<p>Temperatures from my basement and attic.</p>"

# The variable name in Python is used to form variable names in javascript. Any
# dictionary defined in the global namespace of the config file is used as a
# graph config.
fahrenheit = {
	# overall graph title: big letters above the chart area
	'title': 'Temperature (F)',

	# in case of multiple graphs, order on the page
	'order': 1,

	# (optional, defaults to float) parsing function applied to all data in
	# this graph, converts from a string read from the logs to (typically)
	# a number
	'parse': float,

	# (optional, defaults to noop) mapping function applied to all data in
	# this graph; arbitrary conversion (such as voltage numbers to
	# temperatures, for a particular sensor)
	'map': tmp36VoltsToF,

	'series': {
		# which log data set to draw from
		'0x0013a20082fab0-AD0': [
			# a list of series (lines) the data will contribute to
			{
				# name of the series (line) to contribute to
				'title': 'Outside',

				# (optional, defaults to noop) function which
				# adjusts parsed values from the log, applied
				# after parsing and before graph-level mapping;
				# for example, to adjust sensor readings based
				# on calibration
				'preMap': lambda x: x + 0.02,

				# optional most-recent date which will be
				# included for this series
				'lastDate': '2012 Sep 20 04:01:58 UTC',
			},
			{
				# A second series might be used if the same
				# physical sensor were moved: from outside,
				# where it was through the 20th, to inside.
				'title': 'Living Room',
				'preMap': lambda x: x + 0.02,
			},
			...
		],
		...
	},
	# text annotations to appear on this graph
	'annotations': [
		# Aside from the date (x), annotation dicts are dumped
		# wholesale via json and used directly by Dygraphs.
		{
			# series (line) to attach to
			'series': 'Outside',
			# timestamp of a point to attach to
			'x': '2012 Sep 18 08:12:24 UTC',
			# text to show in a box next to the line
			'shortText': 'F',
			# text to show on hover, in a tooltip
			'text': 'first frost',
		},
		...
	],
}
"""

import os
import logging


log = logging.getLogger('webgraph.graphconfig')
_CONFIG_FILE_NAME = 'graphconfig.local.py'
_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__),
		_CONFIG_FILE_NAME)


def checkForLocalConfig():
	"""
	Check that the local graph config file exists. If not, log a warning.
	@return whether the file exists
	"""
	if os.path.isfile(_CONFIG_FILE_PATH):
		return True
	else:
		log.warning('No local graph config file found at %s. A graph'
				+ ' config defines how to map log data to named'
				+ ' lines on a graph; for details, see %s.',
				_CONFIG_FILE_PATH, __file__)
		return False


def _graphConfigCmp((nameA, configA), (nameB, configB)):
	orderA = configA.get('order')
	orderB = configB.get('order')
	if orderA == orderB:
		return 0
	elif orderA is None:
		return -1
	else:
		return orderA.__cmp__(orderB)


def getConfigsAndHtml():
	"""
	Get configuration data for graphs. This executes %s
	and treats any dictionaries defined therein as graph configs; and this
	looks for the special variable 'html', for a raw HTML blob.

	@return a tumple of (dict of {variableName: graphConfig},
		string or None) which are the graph configs and an optional
		HTML blob
	"""
	localNs = {}
	graphConfigs = []
	if not checkForLocalConfig():
		return graphConfigs, None
	try:
		execfile(_CONFIG_FILE_PATH, globals(), localNs)
	except:
		log.error('error loading graph configs from %s'
				% _CONFIG_FILE_PATH, exc_info=True)
		return graphConfigs, None

	for name, value in localNs.iteritems():
		if isinstance(value, dict):
			graphConfigs.append((name, value))
	graphConfigs.sort(cmp=_graphConfigCmp)
	return graphConfigs, localNs.get('html')


getConfigsAndHtml.__doc__ = getConfigsAndHtml.__doc__ % _CONFIG_FILE_NAME


def tmp36VoltsToC(volts):
	"""
	Convert numeric volts to numeric degrees centigrade, for a TMP36.
	"""
        return volts * 100 - 50


def tmp36VoltsToF(volts):
	"""
	Convert numeric volts to numeric degrees Fahrenheit.
	"""
        return tmp36VoltsToC(volts) * (9.0/5.0) + 32

