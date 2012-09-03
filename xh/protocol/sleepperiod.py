from . import Command, CommandRegistry, NumberCommand



class SleepPeriod(NumberCommand):
	"""
	In cyclic sleep, how long the device will sleep at a time. Rounded to
	10ms increments.

	On a parent device, how long to buffer messages for sleepers.

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""
	_MIN = 0x20 # in internal units
	_MAX = 0xAF0
	_EXTERNAL_PER_INTERNAL = 10

	def __init__(self, periodMillis=None, **kwargs):
		NumberCommand.__init__(self, Command.NAME.SP, 'periodMillis',
			unitName='ms', number=periodMillis, **kwargs)



CommandRegistry.put(Command.NAME.SP, SleepPeriod)
