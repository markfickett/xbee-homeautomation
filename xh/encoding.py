"""
Conversion functions to pack/unpack values for XBee API communication.
"""


BYTE_BASE = 0x100
MILLIVOLTS_PER_VOLT = 1e-3
BYTES_PER_SERIAL = 8		# number of bytes in an XBee serial number


def numberToString(n, padToBytes=1):
	"""
	Pack a number of arbitrary size into (little-endian) a string.
	@param padToBytes Left-pad the string with null bytes so that
		it is at least the given number of bytes long.
	Example: 0x3ef7 => '\x3e\xf7'
	"""
	s = ''
	while n > 0:
		lowByte = n % BYTE_BASE
		s = chr(lowByte) + s
		n = n / BYTE_BASE
	if padToBytes is not None and len(s) < padToBytes:
		s = ('\x00'*(padToBytes - len(s))) + s
	return s


def numberToSerialString(n):
	"""
	Pack a number for use as an Xbee module serial number (must be 8 bytes).
	"""
	return numberToString(n, padToBytes=BYTES_PER_SERIAL)


def stringToNumber(s):
	"""
	Unpack a (little-endian) string to a number.
	Example: '>\xf7' => 0x3ef7 or '\n\xe4' => 2788 (0x0ae4)
	"""
	n = 0
	for c in s:
		n *= BYTE_BASE
		n += ord(c)
	return n


def stringToBoolean(s):
	"""
	Unpack a string to boolean. The string is expected to be a packed
	number, where 0 is False and 1 is True.
	"""
	return numberToBoolean(stringToNumber(s))


def numberToBoolean(n):
	"""
	Unpack a number to boolean. The number must be 0 (False) or 1 (True).
	"""
	if n == 0:
		return False
	elif n == 1:
		return True
	else:
		raise ValueError(('Encoded value "%s" is not an expected '
			+ 'boolean value, should be 0 or 1.') % n)


def booleanToString(b):
	return numberToString(b and 1 or 0)


def numberToVolts(n):
	"""
	Convert a number (in internal / API units) to volts read from an analog
	input pin.
	"""
	return n * (1200.0 / 1024.0) * MILLIVOLTS_PER_VOLT


def stringToVolts(s):
	"""
	Unpack a string to a number, and convert that number to volts read from
	an analog input pin.
	"""
	return numberToVolts(stringToNumber(s))


def voltsToNumber(v):
	"""
	Convert from volts to internal / API units.
	"""
	return (v / MILLIVOLTS_PER_VOLT) * (1024.0 / 1200.0)


def bitFieldToIndexSet(bitField):
	"""
	@param bitField encoded as an int
	@return an set containing the indices of the bits which are set in the
		given field.
	Example: 0x43 == b0100 0011 => set([0, 1, 6])
	"""
	b = bitField
	i = 0
	indices = set()
	while b > 0:
		if b & 0x1:
			indices.add(i)
		b = b >> 1
		i += 1
	return indices


def indicesToBitField(indices):
	"""
	Create and return a bit field (as a number) which has the bits with the
	given indices set.
	Example: set([0, 1, 6]) => b0100 0011 == 0x43
	"""
	bitField = 0x0
	for i in indices:
		bitField |= (1 << i)
	return bitField

