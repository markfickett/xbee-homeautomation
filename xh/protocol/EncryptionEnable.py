from .. import Encoding
from . import Command, CommandRegistry



class EncryptionEnable(Command):
	"""
	Whether network encryption is enabled.
	"""


	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.EE, **kwargs)
		self.__enabled = False


	def setEnabled(self, enabled):
		self.__enabled = bool(enabled)


	def getEnabled(self):
		return self.__enabled


	def _formatParameter(self):
		return self._FormatNamedValues({'enabled': self.getEnabled()})


	def parseParameter(self, p):
		self.__enabled = Encoding.StringToBoolean(p)



CommandRegistry.put(Command.NAME.EE, EncryptionEnable)
