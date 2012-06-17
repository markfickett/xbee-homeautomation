from ..deps import Enum



class Frame:
	# ZigBee Mesh frame types, matching the xbee library's names.
	TYPE = Enum(
		# AT command (immediate)	# 0x08 in XBee API
		# AT command (queued)		# 0x09
		# Remote Command Request	# 0x17
		'at_response',			# 0x88
		# Modem Status			# 0x8A
		# TX request			# 0x10
		# TX response			# 0x8B
		# RX received			# 0x90
		'rx_io_data_long_addr',		# 0x92
		# Node Identification Indicator	# 0x95
		'remote_at_response',		# 0x97
	)


	# Python API dict fields common to all frames: the frame type.
	FIELD = Enum('id')


	def __init__(self):
		pass


	def mergeFrom(self, d):
		"""
		Update this Frame with any recognized data in an API dict.
		@param d data from the xbee Python API, unprocessed
		@return a set of all the keys from the dict that were used
		"""
		return set()


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

