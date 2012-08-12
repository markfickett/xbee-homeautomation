import logging
log = logging.getLogger('xh.protocol.Data')

from ..deps import Enum
from .. import Encoding, EnumUtil
from . import Frame, FrameRegistry
import datetime



class Data(Frame):
	FIELD = Enum(
		'source_addr',
		'source_addr_long',
		'samples',
	)


	# Ex: '2012 Jun 17 23:24:18 UTC'
	DATETIME_FORMAT = '%Y %b %d %H:%M:%S UTC'


	def __init__(self, setTimestampToNow=True):
		Frame.__init__(self, frameType=Frame.TYPE.rx_io_data_long_addr)
		self._sourceAddress = None
		self._sourceAddressLong = None
		self._samples = []
		if setTimestampToNow:
			self.setTimestampToNow()
		else:
			self._timestamp = None


	def setTimestampToNow(self):
		self._timestamp = datetime.datetime.utcnow()


	def getTimestamp(self):
		"""
		@return the UTC creation timestamp of the sample data
		"""
		return self._timestamp


	def formatTimestamp(self):
		return datetime.datetime.strftime(
			self.getTimestamp(), self.DATETIME_FORMAT)


	def getSourceAddress(self):
		return self._sourceAddress


	def getSourceAddressLong(self):
		return self._sourceAddressLong


	def getSamples(self):
		return list(self._samples)


	def getNamedValues(self):
		d = Frame.getNamedValues(self)
		samples = self.getSamples()
		if not samples:
			samples = None
		d.update({
			'sourceAddress': self.getSourceAddress(),
			'sourceAddressLong': self.getSourceAddressLong(),
			'samples': samples,
		})
		return d


	def __str__(self):
		s = 'data'
		t = self.getTimestamp()
		if t is None:
			t = ''
		else:
			t = ' ' + self.formatTimestamp()
		return '%s%s%s' % (s, t,
			self._FormatNamedValues(self.getNamedValues()))


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		data = cls()

		sourceAddrKey = str(cls.FIELD.source_addr)
		data._sourceAddress = Encoding.StringToNumber(d[sourceAddrKey])
		usedKeys.add(sourceAddrKey)

		sourceAddrLongKey = str(cls.FIELD.source_addr_long)
		data._sourceAddressLong = Encoding.StringToNumber(
			d[sourceAddrLongKey])
		usedKeys.add(sourceAddrLongKey)

		samplesKey = str(cls.FIELD.samples)
		data._samples = []
		for sd in d[samplesKey]:
			data._samples += Sample.CreateFromDict(sd)
		usedKeys.add(samplesKey)

		return data



class Sample:
	PIN_TYPE = Enum(
		'adc',		# analog sample
		'dio',		# digital sample
	)

	def __init__(self, pinNum, pinType, volts=None, bit=None):
		self.__pinNum = int(pinNum)

		if pinType not in self.PIN_TYPE:
			raise ValueError('Pin type %r not one of %r.'
				% (pinType, self._PIN_TYPE))
		self.__pinType = pinType

		if volts is None:
			self.__volts = None
		else:
			self.__volts = float(volts)

		if bit is None:
			self.__bit = None
		else:
			self.__bit = bool(bit)


	def getPinNumber(self):
		return self.__pinNum


	def getPinType(self):
		return self.__pinType


	def getVolts(self):
		return self.__volts


	def getBit(self):
		return self.__bit


	def __str__(self):
		valueStr = ','
		if self.__volts is not None:
			valueStr = valueStr + ' volts=%.3f' % self.__volts
		elif self.__bit is not None:
			valueStr = valueStr + ' ' + str(self.__bit)
		else:
			valueStr = ''

		return 'Sample(%d, %s%s)' % (
			self.__pinNum,
			self.__pinType,
			valueStr,
		)


	@classmethod
	def CreateFromDict(cls, d):
		for key, value in d.iteritems():
			pinType, pinNum = key.split('-')
			pinNum = int(pinNum)
			pinType = EnumUtil.FromString(cls.PIN_TYPE, pinType)
			valueKwargs = {}
			if pinType == cls.PIN_TYPE.adc:
				valueKwargs['volts'] = Encoding.NumberToVolts(
					value)
			elif pinType == cls.PIN_TYPE.dio:
				valueKwargs['bit'] = value
			else:
				raise RuntimeError(('unprepared to convert '
					+ 'value "%s" for pin %s-%d')
					% (value, pinType, pinNum))
			yield Sample(pinNum, pinType, **valueKwargs)



FrameRegistry.put(Frame.TYPE.rx_io_data_long_addr, Data)
