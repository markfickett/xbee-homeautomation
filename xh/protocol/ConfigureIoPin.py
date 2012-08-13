from ..deps import Enum
from .. import Encoding, Util
from . import Command, CommandRegistry, PIN, PIN_NAME_TO_NUMBER



class ConfigureIoPin(Command):
	"""
	The function of one of the digital and/or analog IO pins.

	See I/O Commands, pages 133-5 of the Xbee Series 2 Datasheet.
	"""


	# all available functions, across all pins
	FUNCTION = Enum(
		'DISABLED',
		'UNMONITORED_INPUT',	# digital input

		'CTS',		# flow control
		'RTS',		# flow control
		'RSSI',
		'COMM',		# commissioning button enabled
		'ASSOC',	# associated indication LED

		'ANALOG_INPUT',

		'DIGITAL_INPUT',

		'DIGITAL_OUTPUT_LOW',

		'DIGITAL_OUTPUT_HIGH',

		'RS485_TX_ENABLE_LOW',	# RS-485 transmit enable (low enable)

		'RS485_TX_ENABLE_HIGH',
	)


	# the numeric value which each function is encoded as
	FUNCTION_TO_VALUE = {
		FUNCTION.DISABLED:		0,
		FUNCTION.UNMONITORED_INPUT:	0,

		FUNCTION.CTS:			1,
		FUNCTION.RTS:			1,
		FUNCTION.RSSI:			1,
		FUNCTION.COMM:			1,
		FUNCTION.ASSOC:			1,

		FUNCTION.ANALOG_INPUT:		2,

		FUNCTION.DIGITAL_INPUT:		3,

		FUNCTION.DIGITAL_OUTPUT_LOW:	4,

		FUNCTION.DIGITAL_OUTPUT_HIGH:	5,

		FUNCTION.RS485_TX_ENABLE_LOW:	6,

		FUNCTION.RS485_TX_ENABLE_HIGH:	7,
	}
	VALUE_TO_FUNCTIONS = Util.InvertedDictWithRepeatedValues(
		FUNCTION_TO_VALUE)


	# which command acts on which pin (by name, for readability)
	_COMMAND_NAME_TO_A_PIN_NAME = {
		Command.NAME.D0:	PIN.DIO0,	# and AD0 / COMM
		Command.NAME.D1:	PIN.DIO1,	# and AD1
		Command.NAME.D2:	PIN.DIO2,	# and AD2
		Command.NAME.D3:	PIN.DIO3,	# and AD3
		Command.NAME.D4:	PIN.DIO4,
		Command.NAME.D5:	PIN.DIO5,	# and ASSOC
		Command.NAME.D6:	PIN.DIO6,	# and RTS
		Command.NAME.D7:	PIN.DIO7,	# and CTS
		Command.NAME.P0:	PIN.DIO10,	# and PWM / RSSI
		Command.NAME.P1:	PIN.DIO11,
		Command.NAME.P2:	PIN.DIO12,
	}
	COMMAND_NAME_TO_PIN_NUMBER = {}
	for cmd, pin in _COMMAND_NAME_TO_A_PIN_NAME.iteritems():
		COMMAND_NAME_TO_PIN_NUMBER[cmd] = PIN_NAME_TO_NUMBER[pin]
	PIN_NUMBER_TO_COMMAND_NAME = Util.InvertedDict(
		COMMAND_NAME_TO_PIN_NUMBER)


	# map from each pin to the functions it may have
	# aliases
	__D = (
		FUNCTION.DIGITAL_INPUT,
		FUNCTION.DIGITAL_OUTPUT_LOW,
		FUNCTION.DIGITAL_OUTPUT_HIGH,
	)
	__D_OR_DISABLED = __D + (FUNCTION.DISABLED,)
	__D_OR_UNMONITORED = __D + (FUNCTION.UNMONITORED_INPUT,)
	__A_OR_D_OR_DISABLED = __D_OR_DISABLED + (FUNCTION.ANALOG_INPUT,)
	# main map (defined on name for readability)
	_A_PIN_NAME_TO_FUNCTIONS = {
		PIN.DIO7: (
			FUNCTION.CTS,
			FUNCTION.RS485_TX_ENABLE_LOW,
			FUNCTION.RS485_TX_ENABLE_HIGH,
		) + __D_OR_DISABLED,
		PIN.DIO6: (FUNCTION.RTS,) + __D_OR_DISABLED,
		PIN.PWM0: (FUNCTION.RSSI,) + __D_OR_DISABLED,
		PIN.DIO11: __D_OR_UNMONITORED,
		PIN.DIO12: __D_OR_UNMONITORED,
		PIN.AD0: __D + (FUNCTION.COMM, FUNCTION.ANALOG_INPUT),
		PIN.AD1: __A_OR_D_OR_DISABLED,
		PIN.AD2: __A_OR_D_OR_DISABLED,
		PIN.AD3: __A_OR_D_OR_DISABLED,
		PIN.DIO4: __D_OR_DISABLED,
		PIN.ASSOC: (FUNCTION.ASSOC,) + __D_OR_DISABLED,
	}
	PIN_NUMBER_TO_FUNCTIONS = {}
	for pinName, fns in _A_PIN_NAME_TO_FUNCTIONS.iteritems():
		PIN_NUMBER_TO_FUNCTIONS[PIN_NAME_TO_NUMBER[pinName]] = fns


	def __init__(self, pinName=None, pinNumber=None, fromCommandName=None,
		function=None, **kwargs):

		if len(filter(lambda x: x is not None,
		[pinName, pinNumber, fromCommandName])) != 1:
			raise ValueError(('Exactly one of pinName (%r) and '
				+ 'pinNumber (%r) and fromCommandName (%r) must'
				+ ' be defined.')
				% (pinName, pinNumber, fromCommandName))

		if fromCommandName is not None:
			cmd = fromCommandName
			self.__pinNumber = self.COMMAND_NAME_TO_PIN_NUMBER[cmd]
			self.__pinName = self._COMMAND_NAME_TO_A_PIN_NAME[cmd]
		else:
			if pinNumber is None:
				self.__pinNumber = PIN_NAME_TO_NUMBER[pinName]
				self.__pinName = pinName
			else:
				self.__pinName = PIN_NUMBER_TO_NAMES[
					pinNumber][0]
				self.__pinNumber = pinNumber
			cmd = self.PIN_NUMBER_TO_COMMAND_NAME[self.__pinNumber]

		Command.__init__(self, cmd, **kwargs)

		if function is not None:
			self.setFunction(function)
		else:
			self.__function = None


	def getPinName(self):
		return self.__pinName


	def getPinNumber(self):
		return self.__pinNumber


	def parseParameter(self, p):
		functionNum = Encoding.StringToNumber(p)
		self.setParameter(functionNum)

		interpretations = set(self.VALUE_TO_FUNCTIONS[functionNum])
		available = set(self.PIN_NUMBER_TO_FUNCTIONS[
			self.getPinNumber()])
		functions = interpretations.intersection(available)

		if len(functions) != 1:
			raise ValueError(("Ambiguous or invalid function number"
			+ " %d for pin %d (%s). Available interpretations %s do"
			+ " not intersect with the pin's available functions %s"
			+ " with 1 result.")
			% (functionNum, self.getPinNumber(), self.getPinName(),
				interpretations, available))

		self.__function = iter(functions).next()


	def getFunction(self):
		return self.__function


	def setFunction(self, f):
		available = set(self.PIN_NUMBER_TO_FUNCTIONS[
			self.getPinNumber()])
		if f not in available:
			raise ValueError(('Function %s is not a valid option '
			+ 'for pin %d (%s). Available functions are %s.')
			% (f, self.getPinNumber(), self.getPinName(),
				available))
		self.__function = f
		self.setParameter(self.FUNCTION_TO_VALUE[self.__function])


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		n = self.getPinNumber()
		n = n and str(n) # Format as decimel, not hex.
		d.update({
			'function': self.getFunction(),
			'pinName': self.getPinName(),
			'pinNumber': n,
		})
		return d



for cmdName in ConfigureIoPin.COMMAND_NAME_TO_PIN_NUMBER.keys():
	CommandRegistry.put(cmdName, ConfigureIoPin)
