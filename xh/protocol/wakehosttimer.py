from . import Command, CommandRegistry, NumberCommand



class WakeHostTimer(NumberCommand):
	"""
	If nonzero, time a device should allow after waking from sleep before
	transmitting I/O samples or sending data out the UART.

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""


	def __init__(self, delayMillis=None, **kwargs):
		NumberCommand.__init__(self, Command.NAME.WH, 'delayMillis',
			unitName='ms', number=delayMillis, **kwargs)



CommandRegistry.put(Command.NAME.WH, WakeHostTimer)
