from ..deps import Enum
from . import DEVICE_TYPE, Frame, FrameRegistry



class NodeId(Frame):
	"""
	Identification information sent by a node. This is sent on various
	occasions, including: when a node joins a network; when the commission
	pin (20) is grounded; and as part of a node-discover response.
	"""
	def __init__(self):
		Frame.__init__(self, frameType=Frame.TYPE.node_id_indicator)

		self.__networkAddress = None
		self.__serial = None
		self.__nodeIdentifier = None
		self.__parentNetworkAddress = None
		self.__deviceType = None
		self.__statusFromReserved = None
		self.__profileId = None
		self.__manufacturerId = None


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		id = NodeId()
		return id


	def _updateFromDict(self, d, usedKeys):
		Frame._updateFromDict(self, d, usedKeys)


	def setNetworkAddress(self, networkAddress):
		self.__networkAddress = int(networkAddress)


	def getNetworkAddress(self):
		return self.__networkAddress


	def setSerial(self, serial):
		self.__serial = int(serial)


	def getSerial(self):
		return self.__serial


	def setNodeIdentifier(self, nodeIdentifier):
		self.__nodeIdentifier = str(nodeIdentifier)


	def getNodeIdentifier(self):
		return self.__nodeIdentifier


	def setParentNetworkAddress(self, pna):
		self.__parentNetworkAddress = int(pna)


	def getParentNetworkAddress(self):
		return self.__parentNetworkAddress


	def setDeviceType(self, deviceType):
		if not (deviceType is None or deviceType in DEVICE_TYPE):
			raise ValueError('Device type %s is not in %s.' %
				(deviceType, DEVICE_TYPE))
		self.__deviceType = deviceType


	def getDeviceType(self):
		return self.__deviceType


	def setStatusFromReserved(self, status):
		self.__statusFromReserved = status


	def getStatusFromReserved(self):
		return self.__statusFromReserved


	def setProfileId(self, profileId):
		self.__profileId = int(profileId)


	def getProfileId(self):
		return self.__profileId


	def setManufacturerId(self, manufacturerId):
		self.__manufacturerId = int(manufacturerId)


	def getManufacturerId(self):
		return self.__manufacturerId


	def __str__(self):
		name = self.getNodeIdentifier()
		if name is not None:
			name = repr(name)
		return self._FormatNamedValues({
			'MY': self.getNetworkAddress(),
			'serial': self.getSerial(),
			'NI': name,
			'parentNetAddr': self.getParentNetworkAddress(),
			'deviceType': self.getDeviceType(),
			'status': self.getStatusFromReserved(),
			'profileId': self.getProfileId(),
			'manufacturerId': self.getManufacturerId(),
		})


FrameRegistry.put(Frame.TYPE.node_id_indicator, NodeId)
