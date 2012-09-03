from .. import encoding
from . import Command



class NumberCommand(Command):
	"""
	Base for a Command that sets/reads a single number.
	"""
	# to be overridden by subclasses
	_MIN = 0
	_MAX = 0xFFFF
	# to convert external units (ex: milliseconds) to internal units
	# (ex: 10ms increments)
	_EXTERNAL_PER_INTERNAL = 1


	def __init__(self, commandName, valueName, unitName=None, number=None,
			**kwargs):
		"""
		@param commandName a Command.NAME value, for Command
		@param valueName to generate getters, like 'delayMillis'
		@param unitName for messages, like 'ms' in '5ms'
		"""
		Command.__init__(self, commandName, **kwargs)
		self.__name = valueName
		self.__getterName = ('get%s'
			% valueName[0].upper() + valueName[1:])
		if number is None:
			self.__num = None
		else:
			iNum = number / self._EXTERNAL_PER_INTERNAL
			u = unitName or ''
			if iNum < self._MIN or iNum > self._MAX:
				raise ValueError(('%s %s%s is not in allowed '
				+ 'range [%d%s, %d%s].')
				% (self.__name, number, u,
				self._MIN * self._EXTERNAL_PER_INTERNAL, u,
				self._MAX * self._EXTERNAL_PER_INTERNAL, u))
			self.__num = iNum


	def __getattr__(self, name):
		if name == self.__getterName:
			return self._get
		else:
			return Command.__getattr__(self, name)


	def _get(self):
		return self.__num and (self.__num * self._EXTERNAL_PER_INTERNAL)


	def parseParameter(self, p):
		self.__num = encoding.StringToNumber(p)


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		v = self._get()
		if v is not None:
			v = str(v)
		d.update({self.__name: v})
		return d

