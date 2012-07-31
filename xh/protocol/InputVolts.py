from .. import Encoding
from . import Command, CommandRegistry



class InputVolts(Command):
	"""
	The voltage level on the Vcc pin.
	"""


	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.__getattribute__('%V'),
			**kwargs)
		self.__volts = None


	def getVolts(self):
		return self.__volts


	def parseParameter(self, p):
		self.__volts = Encoding.StringToVolts(p)


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update({'volts': self.getVolts()})
		return d



CommandRegistry.put(Command.NAME.__getattribute__('%V'), InputVolts)
