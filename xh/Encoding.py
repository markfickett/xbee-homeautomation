"""
Conversion functions to pack/unpack values for XBee API communication.
"""


BYTE_BASE = 0x100
MILLIVOLTS_PER_VOLT = 1e-3
BYTES_PER_SERIAL = 8		# number of bytes in an XBee serial number


def NumberToPrintedString(n):
	"""
	Pack a number as a printed, hex-formatted string.
	"""
	return '%x' % n


def NumberToString(n, padToBytes=1):
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


def NumberToSerialString(n):
	return NumberToString(n, padToBytes=BYTES_PER_SERIAL)


def PrintedStringToNumber(s):
	"""
	Unpack a %x or %s formatted number. (Try to return a hex int, then a
	float.) Example: '3' => 3 or or 'a' => 10 or '2.2' => 2.2
	"""
	try:
		return int(s, 16)
	except ValueError, e:
		return float(s)


def StringToNumber(s):
	"""
	Unpack a (little-endian) string to a number.
	Example: '>\xf7' => 0x3ef7 or '\n\xe4' => 2788 (0x0ae4)
	"""
	n = 0
	for c in s:
		n *= BYTE_BASE
		n += ord(c)
	return n


def StringToBoolean(s):
	"""
	Unpack a string to boolean. The string is expected to be a packed
	number, where 0 is False and 1 is True.
	"""
	n = StringToNumber(s)
	if n == 0:
		return False
	elif n == 1:
		return True
	else:
		raise ValueError(('Encoded value "%s" is not an expected '
			+ 'boolean value, should be 0 or 1.') % s)


def BooleanToString(b):
	return NumberToString(b and 1 or 0)


def NumberToVolts(n):
	"""
	Convert a number to volts on an analog input pin.
	"""
	return n * (1200.0 / 1024.0) * MILLIVOLTS_PER_VOLT


def StringToVolts(s):
	"""
	Unpack a string to a number, and convert that number to volts on
	an analog input pin.
	"""
	return NumberToVolts(StringToNumber(s))


def VoltsToNumber(v):
	"""
	Convert from volts to internal / API units.
	"""
	return (v / MILLIVOLTS_PER_VOLT) * (1024.0 / 1200.0)


def BitFieldToIndexSet(bitField):
	"""
	@param bitField encoded as a byte string
	@return an set containing the indices of the bits which are set in the
		given field.
	Example: 0x43 == b0100 0011 => set([0, 1, 6])
	"""
	b = StringToNumber(bitField)
	i = 0
	indices = set()
	while b > 0:
		if b & 0x1:
			indices.add(i)
		b = b >> 1
		i += 1
	return indices


def IndicesToBitField(indices):
	bitField = 0x0
	for i in indices:
		bitField |= (1 << i)
	return bitField

