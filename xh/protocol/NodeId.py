from .. import encoding
from ..deps import Enum
from . import DEVICE_TYPE, Frame, FrameRegistry



class NodeId(Frame):
	# The fields expected to be in a node ID dict.
	FIELD = Enum(
		# ASCII name
		'node_id',

		# 16-bit network address of the node's parent
		'parent_source_addr',

		# number from DEVICE_TYPE
		'device_type',

		# number
		'digi_profile_id',

		# number
		'manufacturer_id',

		# cause for sending Node ID (1-indexed)
		'source_event',

		# 16-bit address of remote module that transmitted ID frame
		'source_addr',

		# 64-bit
		'source_addr_long',

		# 16-bit address of sender
		'sender_addr',

		# 64-bit
		'sender_addr_long',
	)

	# causes for sending the Node ID; order is required
	EVENT = Enum(
		# node identification pushbutton event (see D0 command)
		'BUTTON',	# 1

		# after joining event occurred (see JN command)
		'JOIN',		# 2

		# after power cycle event occurred (see JN command)
		'POWER_CYCLE',	# 3
	)

	"""
	Identification information sent by a node. This is sent on various
	occasions, including: when a node joins a network; when the commission
	pin (20) is grounded; and as part of a node-discover response.

	See page 117 of the XBee Series 2 datasheet.
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

		# only set for a Node ID event, not as part of NodeDiscover
		self.__sourceEvent = None
		self.__senderNetworkAddress = None
		self.__senderSerial = None


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		id = NodeId()
		return id


	def _updateFromDict(self, d, usedKeys):
		Frame._updateFromDict(self, d, usedKeys)

		nodeIdKey = str(NodeId.FIELD.node_id)
		self.setNodeIdentifier(d[nodeIdKey])
		usedKeys.add(nodeIdKey)

		parentAddrKey = str(NodeId.FIELD.parent_source_addr)
		self.setParentNetworkAddress(
			encoding.StringToNumber(d[parentAddrKey]))
		usedKeys.add(parentAddrKey)

		deviceTypeKey = str(NodeId.FIELD.device_type)
		self.setDeviceType(DEVICE_TYPE[
			encoding.StringToNumber(d[deviceTypeKey])])
		usedKeys.add(deviceTypeKey)

		profileKey = str(NodeId.FIELD.digi_profile_id)
		self.setProfileId(encoding.StringToNumber(d[profileKey]))
		usedKeys.add(profileKey)

		manuKey = str(NodeId.FIELD.manufacturer_id)
		self.setManufacturerId(encoding.StringToNumber(d[manuKey]))
		usedKeys.add(manuKey)

		srcKey = str(NodeId.FIELD.source_event)
		self.setSourceEvent(NodeId.EVENT[
			encoding.StringToNumber(d[srcKey]) - 1])
		usedKeys.add(srcKey)

		addrKey = str(NodeId.FIELD.source_addr)
		self.setNetworkAddress(encoding.StringToNumber(d[addrKey]))
		usedKeys.add(addrKey)

		serKey = str(NodeId.FIELD.source_addr_long)
		self.setSerial(encoding.StringToNumber(d[serKey]))
		usedKeys.add(serKey)

		sAddrKey = str(NodeId.FIELD.sender_addr)
		self.setSenderNetworkAddress(
			encoding.StringToNumber(d[sAddrKey]))
		usedKeys.add(sAddrKey)

		sSerKey = str(NodeId.FIELD.sender_addr_long)
		self.setSenderSerial(encoding.StringToNumber(d[sSerKey]))
		usedKeys.add(sSerKey)


	def setNetworkAddress(self, networkAddress):
		self.__networkAddress = int(networkAddress)


	def getNetworkAddress(self):
		"""The (original transmitter's) 16-bit network address."""
		return self.__networkAddress


	def setSerial(self, serial):
		self.__serial = int(serial)


	def getSerial(self):
		"""
		The (original transmitter's) 64-bit network address /
		serial number.
		"""
		return self.__serial


	def setSenderNetworkAddress(self, addr):
		self.__senderNetworkAddress = int(addr)


	def getSenderNetworkAddress(self):
		"""The Node ID frame sender's 16-bit network address."""
		return self.__senderNetworkAddress


	def setSenderSerial(self, serial):
		self.__senderSerial = int(serial)


	def getSenderSerial(self):
		"""
		The Node ID frame sender's 64-bit network address /
		serial number.
		"""
		return self.__senderSerial


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


	def setSourceEvent(self, event):
		if not (event is None or event in NodeId.EVENT):
			raise ValueError('Source event %s is not in %s.' %
				(event, NodeId.EVENT))
		self.__sourceEvent = event


	def getSourceEvent(self):
		return self.__sourceEvent


	def getNamedValues(self):
		d = Frame.getNamedValues(self)
		name = self.getNodeIdentifier()
		if name is not None:
			name = repr(name)
		d.update({
			'addr': self.getNetworkAddress(),
			'serial': self.getSerial(),
			'NI': name,
			'parentAddr': self.getParentNetworkAddress(),
			'deviceType': self.getDeviceType(),
			'status': self.getStatusFromReserved(),
			'profileId': self.getProfileId(),
			'manufacturerId': self.getManufacturerId(),
			'sourceEvent': self.getSourceEvent(),
			'senderAddr': self.getSenderNetworkAddress(),
			'senderSerial': self.getSenderSerial(),
		})
		return d


	def __str__(self):
		values = self._FormatNamedValues(self.getNamedValues())
		return 'NodeId%s' % (values or ' (empty)')


FrameRegistry.put(Frame.TYPE.node_id_indicator, NodeId)
