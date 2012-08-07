from . import Command, CommandRegistry



class PullUpResistor(Command):
	"""
	Sets/reads the IO pins for which the internal 30k pull-up resistors
	are enabled.

	See Xbee Series 2 datasheet, page 135.
	"""


	_PIN_NUMBER_ORDER = (
		11,	# bit at index 0 in bit field
		17,
		18,
		19,
		20,
		16,
		9,
		3,
		15,
		13,
		4,
		6,
		7,
		12,	# 13
	)


	@classmethod
	def _PinNumberToBitFieldIndex(cls, pinNumber):
		try:
			return cls._PIN_NUMBER_ORDER.index(pinNumber)
		except ValueError:
			raise ValueError(('Pin number %r is not in the pull-up'
				+ ' resistor bit field. Valid pins are %s.')
				% (pinNumber, set(cls._PIN_NUMBER_ORDER)))


	_BIT_FIELD_ALL_ON = (1 << len(_PIN_NUMBER_ORDER)) - 1


	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.PR, **kwargs)
		self.__bitField = None


	def getBitField(self):
		return self.__bitField


	def setBitField(self, bitField):
		if (bitField & self._BIT_FIELD_ALL_ON) != bitField:
			raise ValueError(('Bit field 0x%X contains bits 0x%X '
				+ 'which are outside expected field with %d'
				+ ' bits (0x%X).')
				% (bitField,
				bitField & (~self._BIT_FIELD_ALL_ON),
				len(self._PIN_NUMBER_ORDER),
				self._BIT_FIELD_ALL_ON))
		self.__bitField = bitField


	def setBitFieldFromPinNumbers(self, pinNumbers):
		bitField = 0x0
		for p in pinNumbers:
			i = self._PinNumberToBitFieldIndex(p)
			bitField |= (1 << i)
		self.setBitField(bitField)


	def getPinNumbersFromBitField(self):
		b = self.getBitField()
		if b is None:
			return None
		pins = set()
		i = 0
		while b > 0:
			if b & 0x1:
				pins.add(self._PIN_NUMBER_ORDER[i])
			b = b >> 1
			i += 1
		return pins


	def parseParameter(self, p):
		self.setBitField(Encoding.StringToNumber(p))


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update({
			'bitField': self.getBitField(),
			'enabledPins': self.getPinNumbersFromBitField(),
		})
		return d



CommandRegistry.put(Command.NAME.PR, PullUpResistor)
