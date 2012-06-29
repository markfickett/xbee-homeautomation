from ..deps import Enum
from . import Registry



class Frame:
	# ZigBee Mesh frame types, matching the xbee library's names.
	# See: http://code.google.com/p/python-xbee/source/browse/xbee/zigbee.py
	TYPE = Enum(
		'at',				# 0x08 in XBee API
		# AT command (queued)		# 0x09
		# Remote Command Request	# 0x17
		'at_response',			# 0x88
		# Modem Status			# 0x8A
		# TX request			# 0x10
		# TX response			# 0x8B
		# RX received			# 0x90
		'rx_io_data_long_addr',		# 0x92
		'node_id_indicator',		# 0x95
		'remote_at_response',		# 0x97
	)


	# Python API dict fields common to all frames: the frame type.
	FIELD = Enum('id')


	def __init__(self, frameType=None):
		if not (frameType is None or frameType in self.TYPE):
			raise ValueError(('Frame type %s is neither None nor '
				+ 'one of the TYPE enum values.') % frameType)
		self.__frameType = frameType


	def getFrameType(self):
		return self.__frameType


	@classmethod
	def CreateFromDict(cls, d, usedKeys):
		"""
		Create a new instance of a Frame subclass. This calls protected
		methods which subclasses should/may override.
		@see _CreateFromDict, _updateFromDict
		@param d an API dict from which to draw values
		@param usedKeys a set to which to add the names of any used
			keys, naming keys for values from the API dict
		"""
		frame = cls._CreateFromDict(d, usedKeys)
		frame._updateFromDict(d, usedKeys)
		return frame


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		"""
		Create a new instance of a Frame subclass. Frame subclasses
		must override this.
		@param d an API dict from which to initialize the frame
		@param usedKeys a set to which to add any keys used; key names
			are those in the API dict which are read
		"""
		raise NotImplementedError()


	def _updateFromDict(self, d, usedKeys):
		"""
		Update this Frame with any recognized data in an API dict.
		Subclasses may override (and call) this.
		@param d data from the xbee Python API, unprocessed
		@param usedKeys a set to update with any keys from the API dict
			which were used
		"""


	@staticmethod
	def _FormatNamedValues(d):
		"""
		{'a': 29, 'b': None, 'c':'XBee'} -> ' a=0x1d c=XBee'
		"""
		s = ''
		for k, v in d.iteritems():
			if v is None:
				continue
			elif type(v) is int:
				formattedV = '0x%x' % v
			elif type(v) is list:
				formattedV = ('['
					+ ', '.join([str(i) for i in v]) + ']')
			else:
				formattedV = str(v)
			s = '%s %s=%s' % (s, k, formattedV)
		return s



FrameRegistry = Registry(Frame.TYPE)
FrameRegistry.__doc__ = 'Which Frame.TYPE is to be parsed by which class.'
