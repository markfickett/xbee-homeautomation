from .. import encoding
from . import Command, CommandRegistry


class SampleRate(Command):
	"""
	The IO sample rate, for periodic sampling, used if at least one digital
	or analog pin has sampling enabled.
	"""
	RATE_DISABLED = 0
	RATE_MIN = 0x32
	RATE_MAX = 0xFFFF


	def __init__(self, sampleRateMillis=None, disableSampling=False,
		**kwargs):
		if disableSampling and (sampleRateMillis is not None):
			raise ValueError(
				'Cannot both disable and set sample rate.')

		Command.__init__(self, Command.NAME.IR, **kwargs)

		self.__rate = None
		self.__disabled = False
		if disableSampling:
			self.disableSampling()
		elif sampleRateMillis is not None:
			self.setSampleRateMillis(sampleRateMillis)


	def disableSampling(self):
		self.__rate = None
		self.__disabled = True
		self.setParameter(self.RATE_DISABLED)


	def isSamplingDisabled(self):
		return self.__disabled


	def setSampleRateMillis(self, rate):
		rateNum = int(rate)
		if rateNum < self.RATE_MIN:
			raise ValueError(('Sampling rate of %dms (from %r) '
				+ 'is less than minimum rate of %dms.')
				% (rateNum, rate, self.RATE_MIN))
		elif rateNum > self.RATE_MAX:
			raise ValueError(('Sampling rate of %dms (from %r) '
				+ 'is more than maximum rate of %dms.')
				% (rateNum, rate, self.RATE_MAX))
		self.__rate = rateNum
		self.__disabled = False
		self.setParameter(self.__rate)


	def getSampleRateMillis(self):
		return self.__rate


	def parseParameter(self, p):
		rateValue = encoding.StringToNumber(p)
		if rateValue == self.RATE_DISABLED:
			self.disableSampling()
		else:
			self.setSampleRateMillis(rateValue)


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		rate = self.getSampleRateMillis()
		if rate is not None:
			rate = '%dms' % rate
		disabled = self.isSamplingDisabled() or None
		d.update({
			'rate': rate,
			'disabled': disabled,
		})
		return d



CommandRegistry.put(Command.NAME.IR, SampleRate)
