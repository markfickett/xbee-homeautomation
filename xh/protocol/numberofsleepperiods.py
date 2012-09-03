from . import Command, CommandRegistry, NumberCommand



class NumberOfSleepPeriods(NumberCommand):
	"""
	Number of sleep periods to not assert PIN.ON if no RF data is waiting.
	May be from 1 (default) to 65535 (0xFFFF).

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""
	_MIN = 1

	def __init__(self, numPeriods=None, **kwargs):
		NumberCommand.__init__(self, Command.NAME.SN, 'numPeriods',
			number=numPeriods, **kwargs)



CommandRegistry.put(Command.NAME.SN, NumberOfSleepPeriods)
