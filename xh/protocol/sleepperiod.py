from . import Command, CommandRegistry, NumberCommand



class SleepPeriod(NumberCommand):
	"""
	In cyclic sleep, how long the device will sleep at a time. Valid values
	are 320ms (the default) to 28s, rounded to 10s increments.

	On a parent device, this specifies how long to buffer messages for
	sleepers. (The actual timeout is 1.2x the specified value, so the
	maximum is 30s.)

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""
	_MIN = 0x20 # in internal units
	_MAX = 0xAF0
	_EXTERNAL_PER_INTERNAL = 10
	DEFAULT_PERIOD_MILLIS = 0x20 * _EXTERNAL_PER_INTERNAL

	def __init__(self, periodMillis=None, **kwargs):
		NumberCommand.__init__(self, Command.NAME.SP, 'periodMillis',
			unitName='ms', number=periodMillis, **kwargs)



CommandRegistry.put(Command.NAME.SP, SleepPeriod)
