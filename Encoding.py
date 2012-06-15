"""
Conversion functions to pack/unpack values for XBee API communication.
"""

def NumberToString(n):
	"""
	Pack numbers of arbitrary size into (little-endian) strings.
	Example: 0x3ef7 => '\x3e\xf7'
	"""
	s = ''
	while n > 0:
		lowByte = n % 0x100
		s = chr(lowByte) + s
		n = n / 0x100
	return s
