import logging

from .. import encoding
from . import Command, CommandRegistry


log = logging.getLogger('VoltageSupplyThreshold')



class VoltageSupplyThreshold(Command):
	"""
	If the supply voltage falls <= this threshold, it will be included
	in I/O samples.

	See page 135 of the Xbee Series 2 datasheet.
	"""
	__THRESHOLD_MAX = encoding.NumberToVolts(0xFFFF)

	# recommended useful extrema from Xbee Series 2 datasheet,
	# which are also more extreme than pro or S2B models
	__XBEE_VOLTAGE_SUPPLY_MIN = 2.1
	__XBEE_VOLTAGE_SUPPLY_MAX = 3.6


	def __init__(self, thresholdVolts=None, **kwargs):
		Command.__init__(self, Command.NAME.__getattribute__('V+'),
			**kwargs)

		if thresholdVolts is None:
			self.__threshold = None
		else:
			self.setThresholdVolts(thresholdVolts)


	def setThresholdVolts(self, threshold):
		if threshold < 0:
			raise ValueError('Threshold must be >= 0 but got %r.'
				% threshold)
		minV, maxV = (self.__XBEE_VOLTAGE_SUPPLY_MIN,
			self.__XBEE_VOLTAGE_SUPPLY_MAX)
		if threshold < minV or threshold > maxV:
			log.warning(('Threshold %r is outside of expected'
			+ ' useful extrema, %.2f to %.2f.')
			% (threshold, minV, maxV))

		self.__threshold = min(threshold, self.__THRESHOLD_MAX)

		self.setParameter(
			int(encoding.VoltsToNumber(self.__threshold)))


	def getThresholdVolts(self):
		return self.__threshold


	def parseParameter(self, p):
		self.__threshold = encoding.StringToVolts(p)


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		v = self.getThresholdVolts()
		if v:
			v = '%.3f' % v
		d.update({'volts': v})
		return d


CommandRegistry.put(Command.NAME.__getattribute__('V+'), VoltageSupplyThreshold)
