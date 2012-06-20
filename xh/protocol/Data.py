import logging
log = logging.getLogger('xh.protocol.Data')

from ..deps import Enum
from .. import Encoding, EnumUtil
from . import Frame
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


	def __init__(self, setTimestamp=True):
		Frame.__init__(self)
		self.__sourceAddress = None
		self.__sourceAddressLong = None
		self.__options = None
		self.__samples = []
		if setTimestamp:
			self.setTimestamp()
		else:
			self.__timestamp = None


	def setTimestamp(self):
		self.__timestamp = datetime.datetime.utcnow()


	def getTimestamp(self):
		"""
		@return the UTC creation timestamp of the sample data
		"""
		return self.__timestamp


	def formatTimestamp(self):
		return datetime.datetime.strftime(
			self.getTimestamp(), self.DATETIME_FORMAT)


	def getSourceAddress(self):
		return self.__sourceAddress


	def getSourceAddressLong(self):
		return self.__sourceAddressLong


	def getOptions(self):
		return self.__options


	def getSamples(self):
		return list(self.__samples)


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


	def mergeFromDict(self, d):
		usedKeys = set()

		sourceAddrKey = str(self.FIELD.source_addr)
		self.__sourceAddress = Encoding.StringToNumber(d[sourceAddrKey])
		usedKeys.add(sourceAddrKey)

		sourceAddrLongKey = str(self.FIELD.source_addr_long)
		self.__sourceAddressLong = Encoding.StringToNumber(
			d[sourceAddrLongKey])
		usedKeys.add(sourceAddrLongKey)

		optionsKey = str(self.FIELD.options)
		self.__options = self.OPTIONS[
			Encoding.StringToNumber(d[optionsKey]) - 1]
		usedKeys.add(optionsKey)

		samplesKey = str(self.FIELD.samples)
		self.__samples = []
		for sd in d[samplesKey]:
			self.__samples += Sample.CreateFromDict(sd)
		usedKeys.add(samplesKey)

		return usedKeys



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



