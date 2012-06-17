from .. import Encoding
from . import Command, DEVICE_TYPE



class NodeDiscover(Command):
	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.ND, **kwargs)
		self.__networkAddress = None
		self.__serial = None
		self.__nodeIdentifier = None
		self.__parentNetworkAddress = None
		self.__deviceType = None
		self.__statusFromReserved = None
		self.__profileId = None
		self.__manufacturerId = None


	def getNetworkAddress(self):
		return self.__networkAddress


	def getSerial(self):
		return self.__serial


	def getNodeIdentifier(self):
		return self.__nodeIdentifier


	def getParentNetworkAddress(self):
		return self.__parentNetworkAddress


	def getDeviceType(self):
		return self.__deviceType


	def getProfileId(self):
		return self.__profileId


	def getManufacturerId(self):
		return self.__manufacturerId


	def _formatParameter(self):
		name = self.getNodeIdentifier()
		if name is not None:
			name = repr(name)
		return self._FormatNamedValues({
			'MY': self.getNetworkAddress(),
			'serial': self.getSerial(),
			'NI': name,
			'parentNetAddr': self.getParentNetworkAddress(),
			'deviceType': self.getDeviceType(),
			'profileId': self.getProfileId(),
			'manufacturerId': self.getManufacturerId(),
		})


	def parseParameter(self, s):
		"""
		Parse out the fields of a node-discovery (ND) response.
		"""
		d = {}
		i = 0
		n = len(s)

		# field (num bytes)

		# network Address (2)
		self.__networkAddress = Encoding.StringToNumber(s[i:i+2])
		i = i + 2

		# serial high (4)
		# serial low (4)
		serial = Encoding.StringToNumber(s[i:i+4])
		i = i + 4
		serial = serial * Encoding.BYTE_BASE**4
		serial = serial + Encoding.StringToNumber(s[i:i+4])
		i = i + 4
		self.__serial = serial

		# node identifier string (null-terminated)
		nameEnd = i
		while nameEnd < n and s[nameEnd] != chr(0):
			nameEnd = nameEnd + 1
		self.__nodeIdentifier = s[i:nameEnd]
		i = nameEnd + 1

		# parent network address (2)
		self.__parentNetworkAddress = Encoding.StringToNumber(s[i:i+2])
		i = i + 2

		# device type (1)
		deviceType = Encoding.StringToNumber(s[i:i+1])
		self.__deviceType = DEVICE_TYPE[deviceType]
		i = i + 1

		# status, "Reserved" (1)
		self.__statusFromReserved = Encoding.StringToNumber(s[i:i+1])
		i = i + 1

		# profile ID (2)
		self.__profileId = Encoding.StringToNumber(s[i:i+2])
		i = i + 2

		# manufacturer ID (2)
		self.__manufacturerId = Encoding.StringToNumber(s[i:i+2])
		i = i + 2

