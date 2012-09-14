from .. import encoding
from . import Command, CommandRegistry, DEVICE_TYPE, NodeId



class NodeDiscover(Command):
	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.ND, **kwargs)
		self.__nodeId = NodeId()


	def getNodeId(self):
		return self.__nodeId


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update(self.__nodeId.getNamedValues())
		return d


	def parseParameter(self, s):
		"""
		Parse out the fields of a node-discovery (ND) response.
		"""
		d = {}
		i = 0
		n = len(s)
		id = self.__nodeId

		# field (num bytes)

		# network Address (2)
		id.setNetworkAddress(encoding.stringToNumber(s[i:i+2]))
		i = i + 2

		# serial high (4)
		# serial low (4)
		serial = encoding.buildSerial(
			encoding.stringToNumber(s[i:i+4]),
			encoding.stringToNumber(s[i+4:i+8]))
		i = i + 8
		id.setSerial(serial)

		# node identifier string (null-terminated)
		nameEnd = i
		while nameEnd < n and s[nameEnd] != chr(0):
			nameEnd = nameEnd + 1
		id.setNodeIdentifier(s[i:nameEnd])
		i = nameEnd + 1

		# parent network address (2)
		id.setParentNetworkAddress(encoding.stringToNumber(s[i:i+2]))
		i = i + 2

		# device type (1)
		deviceType = encoding.stringToNumber(s[i:i+1])
		id.setDeviceType(DEVICE_TYPE[deviceType])
		i = i + 1

		# status, "Reserved" (1)
		id.setStatusFromReserved(encoding.stringToNumber(s[i:i+1]))
		i = i + 1

		# profile ID (2)
		id.setProfileId(encoding.stringToNumber(s[i:i+2]))
		i = i + 2

		# manufacturer ID (2)
		id.setManufacturerId(encoding.stringToNumber(s[i:i+2]))
		i = i + 2



CommandRegistry.put(Command.NAME.ND, NodeDiscover)
