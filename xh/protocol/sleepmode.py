from ..deps import Enum
from .. import encoding, util
from . import Command, CommandRegistry



class SleepMode(Command):
	"""
	Whether to sleep and when to wake.

	Depending on mode, sleep can be controlled by PIN.SLEEP_RQ (pin 9):
	when it is asserted (high), the module will sleep. If commissioning is
	enabled for PIN.COMM/AD0/DIO0, a high-to-low transition will also wake
	a sleeping end device for 30s. When a module is sleeping,
	PIN.ON/PIN.SLEEP (pin 13) is low, and the device will not respond to API
	or AT commands; however, the coordinator and routers will buffer
	commands sent to a sleeping device for 30s.

	If IO samping is enabled (see ConfigureIoPin and SampleRate), a device
	sends samples immediately when it wakes, then according to the sample
	rate while it is awake.

	See pages 85 (sleep details) and 137 (command listing) of the XBee
	series 2 datasheet.
	"""
	MODE = Enum(
		'DISABLED',		# never sleep; be a router
		'PIN_ENABLE',		# sleep when PIN_SLEEP_RQ high
		'CYCLIC',		# sleep on a repeating schedule
		'CYCLIC_PIN_WAKE',	# sleep, but wake when PIN.SLEEP_RQ low
	)

	_MODE_TO_NUM = {
		MODE.DISABLED: 0,
		MODE.PIN_ENABLE: 1,
		MODE.CYCLIC: 4,
		MODE.CYCLIC_PIN_WAKE: 5,
	}

	_NUM_TO_MODE = util.InvertedDict(_MODE_TO_NUM)


	def __init__(self, mode=None, **kwargs):
		Command.__init__(self, Command.NAME.SM, **kwargs)
		if mode is None:
			self.__mode = None
		else:
			if mode not in self.MODE:
				raise ValueError(
					'Given mode %s not one of %s.'
					% (mode, self.MODE))
			self.__mode = mode
			self.setParameter(self._MODE_TO_NUM[self.__mode])


	def getMode(self):
		return self.__mode


	def parseParameter(self, p):
		self.__mode = self._NUM_TO_MODE[encoding.StringToNumber(p)]


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update({'mode': self.getMode()})
		return d



CommandRegistry.put(Command.NAME.SM, SleepMode)
