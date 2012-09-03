from . import Command, CommandRegistry, NumberCommand



class NodeDiscoveryTimeout(NumberCommand):
	"""
	The timeout after a NodeDiscover command is sent within which all nodes
	must respond. See page 130 of the Xbee series 2 datasheet.
	"""
	_MIN = 0x20
	_MAX = 0xFF
	_EXTERNAL_PER_INTERNAL = 100


	def __init__(self, timeoutMillis=None, **kwargs):
		"""
		@param timeoutMillis rounded to the nearest 100ms
		"""
		NumberCommand.__init__(self, Command.NAME.NT, 'timeoutMillis',
			unitName='ms', number=timeoutMillis, **kwargs)



CommandRegistry.put(Command.NAME.NT, NodeDiscoveryTimeout)
