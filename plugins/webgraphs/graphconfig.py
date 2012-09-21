import os
import logging


log = logging.getLogger('webgraph.graphconfig')
_CONFIG_FILE_NAME = 'graphconfig.local.py'
_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__),
		_CONFIG_FILE_NAME)


def _graphConfigCmp((nameA, configA), (nameB, configB)):
	orderA = configA.get('order')
	orderB = configB.get('order')
	if orderA == orderB:
		return 0
	elif orderA is None:
		return -1
	else:
		return orderA.__cmp__(orderB)


def get():
	"""
	Get configuration data for graphs. This executes %s
	and treats any dictionaries defined therein as graph configs, returning
	a dict of {variableName: graphConfig}.
	"""
	localNs = {}
	graphConfigs = []
	if not os.path.isfile(_CONFIG_FILE_PATH):
		log.warning('no local graph config file %s', _CONFIG_FILE_PATH)
		return graphConfigs
	try:
		execfile(_CONFIG_FILE_PATH, globals(), localNs)
	except:
		log.error('error loading graph configs from %s'
				% _CONFIG_FILE_PATH, exc_info=True)
		return graphConfigs

	for name, value in localNs.iteritems():
		if isinstance(value, dict):
			graphConfigs.append((name, value))
	graphConfigs.sort(cmp=_graphConfigCmp)
	return graphConfigs


get.__doc__ = get.__doc__ % _CONFIG_FILE_NAME


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

