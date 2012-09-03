from . import Command, CommandRegistry, NumberCommand



class TimeBeforeSleep(NumberCommand):
	"""
	How long a device should stay awake, after RF or serial data is
	received, before sleeping again. (For cyclic sleep only.) Default: 5s.

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""
	_MIN = 1
	_MAX = 0xFFFE


	def __init__(self, delayMillis=None, **kwargs):
		NumberCommand.__init__(self, Command.NAME.ST, 'delayMillis',
			number=delayMillis, unitName='ms', **kwargs)



CommandRegistry.put(Command.NAME.ST, TimeBeforeSleep)
