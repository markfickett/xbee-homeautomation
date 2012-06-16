"""
Convert to/from XBee API protocol values.
"""

__all__ = [
	'DATA_FIELD',
	'COMMAND',
	'STATUS',
	'DEVICE_TYPE',

	'ParseNodeDiscover',
]

import logging
log = logging.getLogger('Protocol')

from xh.deps import Enum
from xh import Encoding

DATA_FIELD = Enum(
	'frame_id',	# sequence; stringified number
	'command',	# command name; ascii
	'parameter',	# value sent with or received from command; packed
	'status',	# status code; packed
)

COMMAND = Enum(
	'ND',	# Node Discover
)

STATUS = Enum(
	'OK',			# must be index 0
	'ERROR',		# 1
	'INVALID_COMMAND',	# 2
	'INVALID_PARAMETER',	# 3
	'TRANSMIT_FAILURE',	# 4
)

DEVICE_TYPE = Enum(
	'COORDINATOR',	# must be index 0
	'ROUTER',	# 1
	'END_DEVICE',	# 2
)

def ParseNodeDiscover(s):
	"""
	Parse out the fields of a node-discovery (ND) response.
	"""
	d = {}
	i = 0
	n = len(s)

	# field (num bytes)

	# network Address (2)
	d['MY'] = Encoding.StringToNumber(s[i:i+2])
	i = i + 2
	log.debug('MY: 0x%x' % d['MY'])

	# serial high (4)
	# serial low (4)
	serial = Encoding.StringToNumber(s[i:i+4])
	i = i + 4
	serial = serial * Encoding.BYTE_BASE**4
	serial = serial + Encoding.StringToNumber(s[i:i+4])
	i = i + 4
	d['SERIAL'] = serial
	log.debug('serial: 0x%x' % serial)

	# node identifier string (null-terminated)
	nameEnd = i
	while nameEnd < n and s[nameEnd] != chr(0):
		nameEnd = nameEnd + 1
	d['NI'] = s[i:nameEnd]
	i = nameEnd + 1

	# parent network address (2)
	d['PARENT_NETWORK ADDRESS'] = Encoding.StringToNumber(s[i:i+2])
	i = i + 2

	# device type (1)
	deviceType = Encoding.StringToNumber(s[i:i+1])
	d['DEVICE_TYPE'] = DEVICE_TYPE[deviceType]
	i = i + 1

	# status, "Reserved" (1)
	d['STATUS'] = Encoding.StringToNumber(s[i:i+1])
	i = i + 1

	# profile ID (2)
	d['PROFILE_ID'] = Encoding.StringToNumber(s[i:i+2])
	i = i + 2

	# manufacturer ID (2)
	d['MANUFACTURER_ID'] = Encoding.StringToNumber(s[i:i+2])
	i = i + 2

	return d

