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
		'options',
		'samples',
	)


	# receive options; about a sample packet's arrival
	OPTIONS = Enum(
		# was sent directly to us and was acknowledged
		'ACKNOWLEDGED',

		# was sent to everyone
		'BROADCAST',
	)


	# Ex: '2012 Jun 17 23:24:18 UTC'
	DATETIME_FORMAT = '%Y %b %d %H:%M:%S UTC'


	def __init__(self, setTimestampToNow=True):
		Frame.__init__(self, frameType=Frame.TYPE.rx_io_data_long_addr)
		self._sourceAddress = None
		self._sourceAddressLong = None
		self._options = None
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


	def getOptions(self):
		return self._options


	def getSamples(self):
		return list(self._samples)


	def __str__(self):
		samples = self.getSamples()
		if not samples:
			samples = None
		s = 'data'
		t = self.getTimestamp()
		if t is None:
			t = ''
		else:
			t = ' ' + self.formatTimestamp()
		return '%s%s%s' % (s, t, self._FormatNamedValues({
			'sourceAddress': self.getSourceAddress(),
			'sourceAddressLong': self.getSourceAddressLong(),
			'options': self.getOptions(),
			'samples': samples,
		}))


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

		optionsKey = str(cls.FIELD.options)
		data._options = cls.OPTIONS[
			Encoding.StringToNumber(d[optionsKey]) - 1]
		usedKeys.add(optionsKey)

		samplesKey = str(cls.FIELD.samples)
		data._samples = []
		for sd in d[samplesKey]:
			data._samples += Sample.CreateFromDict(sd)
		usedKeys.add(samplesKey)

		return data



class Sample:
	PIN_TYPE = Enum(
		'adc',		# Analog sample
	)

	def __init__(self, pinNum, pinType, volts=None):
		self.__pinNum = pinNum
		self.__pinType = pinType
		self.__volts = volts


	def getPinNumber(self):
		return self.__pinNum


	def getPinType(self):
		return self.__pinType


	def getVolts(self):
		return self.__volts


	def __str__(self):
		valueStr = ','
		if self.__volts is None:
			valueStr = ''
		else:
			valueStr = valueStr + ' volts=%.3f' % self.__volts

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
			else:
				raise RuntimeError(('unprepared to convert '
					+ 'value "%s" for pin %s-%d')
					% (value, pinType, pinNum))
			yield Sample(pinNum, pinType, **valueKwargs)



FrameRegistry.put(Frame.TYPE.rx_io_data_long_addr, Data)
