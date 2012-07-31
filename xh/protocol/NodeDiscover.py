from .. import Encoding
from . import Command, CommandRegistry, DEVICE_TYPE, NodeId



class NodeDiscover(Command):
	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.ND, **kwargs)
		self.__nodeId = NodeId()


	def getNodeId(self):
		return self.__nodeId


	def _formatParameter(self):
		return str(self.__nodeId)


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
		id.setNetworkAddress(Encoding.StringToNumber(s[i:i+2]))
		i = i + 2

		# serial high (4)
		# serial low (4)
		serial = Encoding.StringToNumber(s[i:i+4])
		i = i + 4
		serial = serial * Encoding.BYTE_BASE**4
		serial = serial + Encoding.StringToNumber(s[i:i+4])
		i = i + 4
		id.setSerial(serial)

		# node identifier string (null-terminated)
		nameEnd = i
		while nameEnd < n and s[nameEnd] != chr(0):
			nameEnd = nameEnd + 1
		id.setNodeIdentifier(s[i:nameEnd])
		i = nameEnd + 1

		# parent network address (2)
		id.setParentNetworkAddress(Encoding.StringToNumber(s[i:i+2]))
		i = i + 2

		# device type (1)
		deviceType = Encoding.StringToNumber(s[i:i+1])
		id.setDeviceType(DEVICE_TYPE[deviceType])
		i = i + 1

		# status, "Reserved" (1)
		id.setStatusFromReserved(Encoding.StringToNumber(s[i:i+1]))
		i = i + 1

		# profile ID (2)
		id.setProfileId(Encoding.StringToNumber(s[i:i+2]))
		i = i + 2

		# manufacturer ID (2)
		id.setManufacturerId(Encoding.StringToNumber(s[i:i+2]))
		i = i + 2



CommandRegistry.put(Command.NAME.ND, NodeDiscover)
