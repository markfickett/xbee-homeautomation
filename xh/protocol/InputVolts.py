from .. import Encoding
from . import Command



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


	def _formatParameter(self):
		v = self.getVolts()
		if v:
			return ' volts=%.3fv' % v
		else:
			return ''

