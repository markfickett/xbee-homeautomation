import ConfigParser, os



class Config:
	"""
	Manager for the configuration/settings which are saved to a file,
	and holder for constants.

	Setup code should have one 'with Config()' block, and other code (called
	from within that block) should call Config.get() to use the singleton
	ConfigParser.
	"""
	SERIAL_BAUD = 9600
	PLUGIN_DIR = 'plugins'
	PLUGIN_INFO_EXTENSION = 'xh-plugin-info'
	CONFIG_FILE_NAME = '~/.xhconfig'


	__ConfigParser = None


	@classmethod
	def get(cls):
		"""
		@return the singleton ConfigParser (which loads/saves mutable
			settings from/to a file), or raises an error if
			the Config context has not been entered
		"""
		if cls.__ConfigParser is None:
			raise RuntimeError('Enter the Config context first.')
		return cls.__ConfigParser


	def _processConfigFileName(self):
		return os.path.expanduser(self.CONFIG_FILE_NAME)


	def __enter__(self):
		if Config.__ConfigParser is not None:
			raise RuntimeError(
				'Only one Config may be in context at a time.')
		Config.__ConfigParser = ConfigParser.SafeConfigParser()
		Config.__ConfigParser.read(self._processConfigFileName())
		return Config.__ConfigParser


	def __exit__(self, t, v, tb):
		with open(self._processConfigFileName(), 'w') as configFile:
			Config.__ConfigParser.write(configFile)
		Config.__ConfigParser = None

