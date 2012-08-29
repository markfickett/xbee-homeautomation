import datetime
import logging

from .. import encoding, enumutil
from ..deps import Enum
from . import Frame, FrameRegistry, PIN, Registry

log = logging.getLogger('xh.protocol.Data')
VCC_BUG_URL = 'http://code.google.com/p/python-xbee/issues/detail?id=35'


__all__ = [
	'Data',

	'Sample',
	'AnalogSample',
	'DigitalSample',
]



class Data(Frame):
	"""
	Automatically sampled values. See SampleRate.

	V+ (Vcc level; see VoltageSupplyThreshold) samples are incorrect, due
	to a bug in xbee-python (analog values are clamped to 0x3FF, see
	%s ). However,
	values returned for other analog pins, and for InputSample, are correct.
	"""


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


	@classmethod
	def FormatTimestamp(cls, timestamp):
		return datetime.datetime.strftime(
			timestamp, cls.DATETIME_FORMAT)


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
			t = ' ' + self.FormatTimestamp(t)
		return '%s%s%s' % (s, t,
			self._FormatNamedValues(self.getNamedValues()))


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		data = cls()

		sourceAddrKey = str(cls.FIELD.source_addr)
		data._sourceAddress = encoding.StringToNumber(d[sourceAddrKey])
		usedKeys.add(sourceAddrKey)

		sourceAddrLongKey = str(cls.FIELD.source_addr_long)
		data._sourceAddressLong = encoding.StringToNumber(
			d[sourceAddrLongKey])
		usedKeys.add(sourceAddrLongKey)

		samplesKey = str(cls.FIELD.samples)
		data._samples = []
		for sd in d[samplesKey]:
			data._samples += Sample.CreateFromDict(sd)
		usedKeys.add(samplesKey)

		return data


Data.__doc__ = Data.__doc__ % VCC_BUG_URL



class Sample:
	PIN_TYPE = Enum(
		'adc',		# analog sample
		'dio',		# digital sample
	)
	_Registry = Registry(PIN_TYPE)


	def __init__(self, pinName):
		if pinName not in PIN:
			raise ValueError('Pin %r not in Constants.PIN Enum.'
				% pinName)
		self.__pinName = pinName


	def getPinName(self):
		return self.__pinName


	def __str__(self):
		return '%s(%s, %s)' % (
			self.__class__.__name__,
			self.getPinName(),
			self._formatValue(),
		)


	@classmethod
	def CreateFromDict(cls, d):
		"""
		Determine whether a samples are analog or digital, then dispatch
		parsing to the appropriate Sample subclass.
		@param d a map of XBee API sample keys (ex: "dio-5") to sample
			values (numeric for analog pins; numeric or boolean for
			digital pins)
		"""
		for key, numericValue in d.iteritems():
			pinTypeStr, pinNum = key.split('-')
			pinNum = int(pinNum)
			pinType = enumutil.FromString(cls.PIN_TYPE, pinTypeStr)

			concreteClass = cls._Registry.get(pinType)
			yield concreteClass.CreateFromRawValues(
				pinNum, numericValue)



class AnalogSample(Sample):
	_PIN_NUM_VCC = 7


	def __init__(self, pinName, volts):
		Sample.__init__(self, pinName)
		self.__volts = float(volts)


	def getVolts(self):
		"""
		Get the voltage measured on the sampled analog pin. Note that
		with the exception of VCC, the maximum value ADC pins can sense
		is 1.2v.
		"""
		return self.__volts


	def _formatValue(self):
		return 'volts=%.3f' % self.getVolts()


	@classmethod
	def CreateFromRawValues(cls, pinNum, numericValue):
		v = encoding.NumberToVolts(numericValue)
		if pinNum == cls._PIN_NUM_VCC:
			pinName = PIN.VCC
			log.warning(('Value %.3fv for %s is probably incorrect!'
			+ ' See %s.')
			% (v, pinName, VCC_BUG_URL))
		else:
			pinName = enumutil.FromString(PIN, 'AD%d' % pinNum)
		return cls(pinName, v)


Sample._Registry.put(Sample.PIN_TYPE.adc, AnalogSample)



class DigitalSample(Sample):
	def __init__(self, pinName, isSet):
		Sample.__init__(self, pinName)
		self.__isSet = bool(isSet)


	def getIsSet(self):
		return self.__isSet


	def _formatValue(self):
		return str(self.getIsSet())


	@classmethod
	def CreateFromRawValues(cls, pinNum, numericValue):
		pinName = enumutil.FromString(PIN, 'DIO%d' % pinNum)
		if numericValue in (True, False):
			bit = numericValue
		else:
			bit = encoding.NumberToBoolean(numericValue)
		return cls(pinName, bit)


Sample._Registry.put(Sample.PIN_TYPE.dio, DigitalSample)



FrameRegistry.put(Frame.TYPE.rx_io_data_long_addr, Data)