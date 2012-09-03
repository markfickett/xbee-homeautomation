from . import Command, CommandRegistry



class Write(Command):
	"""
	Write settings to nonvolatile memory on the device.
	"""
	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.WR, **kwargs)



CommandRegistry.put(Command.NAME.WR, Write)
