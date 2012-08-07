__all__ = [
	'DEVICE_TYPE',

	'PIN',
	'PIN_NAME_TO_NUMBER',
	'PIN_NUMBER_TO_NAMES',
]

from ..deps import Enum
from .. import Util


DEVICE_TYPE = Enum(
	'COORDINATOR',	# must be index 0
	'ROUTER',	# 1
	'END_DEVICE',	# 2
)


# See Xbee Series 2 datasheet page 13 for pin name/number table.
PIN = Enum(
	# Digital I/O Pins
	'DIO0',
	'DIO1',
	'DIO2',
	'DIO3',
	'DIO4',
	'DIO5',
	'DIO6',
	'DIO7',
	'DIO8',
	'DIO9',
	'DIO10',
	'DIO11',
	'DIO12',

	# Analog-to-Digital Input Pins
	'AD0',
	'AD1',
	'AD2',
	'AD3',

	# Named Pins
	'VCC',
	'DOUT',		# UART data out
	'DIN',		# UART data in
	'CONFIG',
	'RESET',
	'RSSI',		# RX Signal Strength Indicator
	'PWM0',
	'DTR',
	'SLEEP_RQ',	# Pin Sleep Control Line
	'GND',
	'CTS',		# Clear-to-Send Flow Control
			# CTS, if enabled, is an output.
	'ON',		# module status indicator
	'SLEEP',	# module status indicator
	'VREF',
	'ASSOC',	# Associated Indicator
	'RTS',		# Request-to-Send Flow Control
			# RTS, if enabled, is an input.
	'COMM',		# Commissioning Button
)


# pin 8 is reserved and not listed
PIN_NAME_TO_NUMBER = {
	# Digital I/O Pins
	PIN.DIO0:	20,
	PIN.DIO1:	19,
	PIN.DIO2:	18,
	PIN.DIO3:	17,
	PIN.DIO4:	11,
	PIN.DIO5:	15,
	PIN.DIO6:	16,
	PIN.DIO7:	12,
	PIN.DIO8:	9,
	PIN.DIO9:	13,
	PIN.DIO10:	6,
	PIN.DIO11:	7,
	PIN.DIO12:	4,

	# Analog-to-Digital Input Pins
	PIN.AD0:	20,
	PIN.AD1:	19,
	PIN.AD2:	18,
	PIN.AD3:	17,

	# Named Pins
	PIN.VCC:	1,
	PIN.DOUT:	2,
	PIN.DIN:	3,
	PIN.CONFIG:	3,
	PIN.RESET:	5,
	PIN.RSSI:	6,
	PIN.PWM0:	6,
	PIN.DTR:	9,
	PIN.SLEEP_RQ:	9,
	PIN.GND:	10,
	PIN.CTS:	12,
	PIN.ON:		13,
	PIN.SLEEP:	13,
	PIN.VREF:	14,
	PIN.ASSOC:	15,
	PIN.RTS:	16,
	PIN.COMM:	20,
}


PIN_NUMBER_TO_NAMES = Util.InvertedDictWithRepeatedValues(PIN_NAME_TO_NUMBER)

