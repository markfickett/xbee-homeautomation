from .. import Encoding
from . import Command, CommandRegistry



class NodeDiscoveryTimeout(Command):
	"""
	The timeout after a NodeDiscover command is sent within which all nodes
	must respond. See page 130 of the Xbee series 2 datasheet.
	"""
	_PARAM_VALUE_MIN = 0x20
	_PARAM_VALUE_MAX = 0xFF
	_MS_PER_PARAM_UNIT = 100


	def __init__(self, timeoutMillis=None, **kwargs):
		"""
		@param timeoutMillis rounded to the nearest 100ms
		"""
		Command.__init__(self, Command.NAME.NT, **kwargs)
		if timeoutMillis is None:
			self.__timeoutMillis = None
		else:
			self.setTimeoutMillis(timeoutMillis)


	def setTimeoutMillis(self, timeoutMillis):
		minMs = self._PARAM_VALUE_MIN * self._MS_PER_PARAM_UNIT
		maxMs = self._PARAM_VALUE_MAX * self._MS_PER_PARAM_UNIT
		ms = int(timeoutMillis)
		if ms < minMs or ms > maxMs:
			raise RuntimeError(('Timeout value %dms is outside '
			+ 'acceptable rante of %dms to %dms.')
			% (ms, minMs, maxMs))
		self.__timeoutMillis = ms
		self.setParameter(ms / self._MS_PER_PARAM_UNIT)


	def getTimeoutMillis(self):
		return self.__timeoutMillis


	def parseParameter(self, p):
		n = Encoding.StringToNumber(p)
		self.__timeoutMillis = n * self._MS_PER_PARAM_UNIT


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		ms = self.getTimeoutMillis()
		if ms is not None:
			ms = str(ms)
		d.update({'timeoutMillis': ms})
		return d



CommandRegistry.put(Command.NAME.NT, NodeDiscoveryTimeout)
