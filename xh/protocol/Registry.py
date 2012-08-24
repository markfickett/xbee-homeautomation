import logging

log = logging.getLogger('xh.protocol.Registry')



class Registry:
	"""
	A dict with guards to ensure that a key is only inserted once, and that
	keys must all be members of a particular collection.
	"""
	def __init__(self, names):
		"""
		@param names the set (or Enum) from which keys must be drawn.
			Membership is checked with the 'in' operator.
		"""
		self.__names = names
		self.__registry = {}


	def _checkName(self, name):
		if name not in self.__names:
			raise ValueError(('Name "%s" not in %s')
				% (name, self.__names))


	def put(self, name, value):
		"""
		Set the value for the given name (key).
		@param name a value from the names given at Registry creation.
		"""
		self._checkName(name)
		if name in self.__registry:
			raise RuntimeError(('Command registry already has an '
				+ 'entry for %s: %s.')
				% (name, self.__registry[name]))
		self.__registry[name] = value


	def get(self, name):
		"""
		@return the value for the given name (key), or None.
		"""
		self._checkName(name)
		return self.__registry.get(name)

