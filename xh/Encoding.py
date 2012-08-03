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


def NumberToString(n, padToBytes=None):
	"""
	Pack a number of arbitrary size into (little-endian) a string.
	@param padToBytes If given, left-pad the string with null bytes so that
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
	Unpack a %s-formatted number. (Try to return an int, then a float.)
	Example: '3' => 3 or '2.2' => 2.2
	"""
	try:
		return int(s)
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

