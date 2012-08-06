
__all__ = [
	'DEVICE_TYPE',

	'PINS',
	'PIN_NAMES_TO_NUMBERS',
]

from ..deps import Enum


DEVICE_TYPE = Enum(
	'COORDINATOR',	# must be index 0
	'ROUTER',	# 1
	'END_DEVICE',	# 2
)


# See Xbee Series 2 datasheet page 13 for pin name/number table.
PINS = Enum(
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
	'PWM',
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
PIN_NAMES_TO_NUMBERS = {
	# Digital I/O Pins
	PINS.DIO0:	20,
	PINS.DIO1:	19,
	PINS.DIO2:	18,
	PINS.DIO3:	17,
	PINS.DIO4:	11,
	PINS.DIO5:	15,
	PINS.DIO6:	16,
	PINS.DIO7:	12,
	PINS.DIO8:	9,
	PINS.DIO9:	13,
	PINS.DIO10:	6,
	PINS.DIO11:	7,
	PINS.DIO12:	4,

	# Analog-to-Digital Input Pins
	PINS.AD0:	20,
	PINS.AD1:	19,
	PINS.AD2:	18,
	PINS.AD3:	17,

	# Named Pins
	PINS.VCC:	1,
	PINS.DOUT:	2,
	PINS.DIN:	3,
	PINS.CONFIG:	3,
	PINS.RESET:	5,
	PINS.RSSI:	6,
	PINS.PWM:	6,
	PINS.DTR:	9,
	PINS.SLEEP_RQ:	9,
	PINS.GND:	10,
	PINS.CTS:	12,
	PINS.ON:	13,
	PINS.SLEEP:	13,
	PINS.VREF:	14,
	PINS.ASSOC:	15,
	PINS.RTS:	16,
	PINS.COMM:	20,
}
